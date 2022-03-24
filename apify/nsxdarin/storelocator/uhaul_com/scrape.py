import re
import json
import threading
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from urllib.parse import urljoin
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("uhaul_com")
thread_local = threading.local()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "connection": "Keep-Alive",
}


def write_output(data):
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1


def get_session(reset=False):
    global thread_local
    # give each thread its own session object
    # if using proxy, each thread's session should have a unique IP
    if not hasattr(thread_local, "session") or reset or thread_local.request_count > 10:
        thread_local.session = SgRequests(retries_with_fresh_proxy_ip=4)
        thread_local.request_count = 0

    return thread_local.session


def fetch(url, reset=False):
    global thread_local
    response = get_session(reset).get(url, headers=headers)
    thread_local.request_count += 1
    return response


def get_state_urls():
    r = fetch("https://www.uhaul.com/Locations/US_and_Canada/")
    soup = BeautifulSoup(r.text, "html.parser")
    states = soup.select("#mainRow li.cell a")
    return [urljoin("https://www.uhaul.com", state["href"]) for state in states]


def get_city_urls(state_urls):
    cities = []
    with ThreadPoolExecutor() as executor:
        logger.info(f"scrape cities with {executor._max_workers} workers")
        futures = [executor.submit(get_cities_in_state, url) for url in state_urls]
        for future in as_completed(futures):
            cities.extend(future.result())

    return cities


def get_cities_in_state(state_url, retry_count=0):
    try:
        r = fetch(state_url, retry_count > 0)
        soup = BeautifulSoup(r.text, "html.parser")
        cities = soup.select("#mainRow li.cell a")
        return [urljoin("https://www.uhaul.com", city["href"]) for city in cities]
    except Exception as e:
        if retry_count < 3:
            return get_cities_in_state(state_url, retry_count + 1)

        logger.error(e)
        return []


def get_location_urls(city_urls):
    locations = []
    with ThreadPoolExecutor() as executor:
        logger.info(f"scrape locations with {executor._max_workers} workers")
        futures = [executor.submit(get_locations_in_city, url) for url in city_urls]
        for future in as_completed(futures):
            locations.extend(future.result())

    return locations


def get_locations_in_city(city_url, retry_count=0):
    try:
        r = fetch(city_url, retry_count > 0)
        soup = BeautifulSoup(r.text, "html.parser")
        scripts = soup.select("script")
        location_script = next(
            filter(lambda script: re.search("entityNum", script.string or ""), scripts),
            None,
        )
        if not location_script:
            return []

        matched = re.search(r"mapPins\s=\s*(\[\{.*\}\])", location_script.string)
        data = json.loads(matched.group(1))
        locations = [loc for loc in data if loc["entityNum"]]

        links = soup.select(".sub-nav a")
        for loc in locations:
            link = next(
                filter(lambda link: re.search(loc["entityNum"], link["href"]), links)
            )
            href = link["href"]
            loc["url"] = (
                urljoin("https://www.uhaul.com", href)
                if "uhaul.com" not in href
                else href
            )

        return locations
    except Exception as e:
        if retry_count < 3:
            return get_locations_in_city(city_url, retry_count + 1)

        logger.error(e)
        return []


MISSING = "<MISSING>"


def get_street_address(address):
    street_address = address.get("streetAddress")
    if not street_address:
        return MISSING

    cleaned = re.sub(r"\s*\(.*\)\s*", "", street_address)
    if not cleaned:
        return MISSING

    return cleaned


def get_country_code(country, postal):
    if country == "United States" or re.search("us", country, re.I):
        return "US"

    if re.search("ca", country, re.I):
        return "CA"

    return MISSING


def get_phone(data):
    phone = data.get("telephone")
    if phone:
        return phone

    contact = data.get("contactPoint") or data.get("ContactPoint")
    if not contact:
        return MISSING

    if isinstance(contact, list):
        if not len(contact):
            return MISSING
        return get(contact[0], "telephone")

    return get(contact, "telephone")


def get_hours(hours):
    if not hours or not len(hours):
        return MISSING

    if isinstance(hours, list):
        return ",".join(hours)

    return hours


def get_hours_from_page(soup):
    hours = soup.find_all("li", itemprop="openingHours")
    if not hours or not len(hours):
        title = soup.find("h4", id="hoursTitle")
        if not title:
            return None

        ul = title.find_next("ul")
        if not ul:
            return None

        hours = ul.find_all("li", recursive=False)

    hours_of_operations = [hour.getText().strip() for hour in hours]

    return ",".join(hour for hour in hours_of_operations if hour)


def get(location, key):
    return location.get(key, MISSING) or MISSING


def get_location(loc, retry_count=0):
    locator_domain = "uhaul.com"
    page_url = loc.get("url")
    store_number = loc.get("entityNum")
    location_type = "<MISSING>"
    lat = loc.get("lat")
    lng = loc.get("long")

    try:
        r = fetch(page_url, retry_count > 0)
        soup = BeautifulSoup(r.text, "html.parser")
        scripts = soup.find_all("script", type="application/ld+json")
        location_script = next(
            filter(lambda script: re.search('"address"', script.string or ""), scripts),
            None,
        )

        if not location_script:
            return None

        data = json.loads(location_script.string)
        location_name = get(data, "name")

        address = get(data, "address")
        street_address = get_street_address(address)
        city = address.get("addressLocality")
        state = address.get("addressRegion")
        postal = address.get("postalCode")
        country_code = get_country_code(address.get("addressCountry"), postal)

        phone = get_phone(data)
        hours = get_hours_from_page(soup) or get_hours(data.get("openingHours"))
        if "Sat" not in hours:
            hours = hours + "; Sat: Closed"
        if "Sun" not in hours:
            hours = hours + "; Sun: Closed"

        return SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours,
            raw_address=address,
        )

    except Exception as e:
        if retry_count < 5:
            return get_location(loc, retry_count + 1)

        logger.error(e)
        return []


def fetch_data():
    states = get_state_urls()
    logger.info(f"states: {len(states)}")
    cities = get_city_urls(states)
    logger.info(f"cities: {len(cities)}")

    completed = 0
    locs = get_location_urls(cities)
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_location, loc) for loc in locs]
        for future in as_completed(futures):
            record = future.result()
            if record:
                completed += 1
                if completed % 100 == 0:
                    logger.info(f"locations found: {completed}")

                yield record

    logger.info(f"locations found: {completed}")


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
