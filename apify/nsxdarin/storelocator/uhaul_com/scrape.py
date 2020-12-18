import re
import csv
import json
import threading
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from urllib.parse import urljoin
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = SgLogSetup().get_logger("uhaul_com")


thread_local = threading.local()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "connection": "Keep-Alive",
}


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        for row in data:
            writer.writerow(row)


def get_session(reset=False):
    # give each thread its own session object
    # if using proxy, each thread's session should have a unique IP
    if (not hasattr(thread_local, "session")) or (reset is True):
        thread_local.session = SgRequests()
    return thread_local.session


def get_state_urls():
    session = get_session()
    url = "https://www.uhaul.com/Locations/US_and_Canada/"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    states = soup.select("#mainRow li.cell a")
    return [urljoin("https://www.uhaul.com", state["href"]) for state in states]


def get_city_urls(state_urls):
    cities = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_cities_in_state, url) for url in state_urls]
        for result in as_completed(futures):
            cities.extend(result.result())
    return cities


def get_cities_in_state(state_url, retry_count=0, reset_session=False):
    try:
        session = get_session(reset_session)
        r = session.get(state_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        cities = soup.select("#mainRow li.cell a")
        return [urljoin("https://www.uhaul.com", city["href"]) for city in cities]
    except Exception as e:
        logger.error(e)
        if retry_count < 3:
            return get_cities_in_state(state_url, retry_count + 1, True)
        else:
            return []


def get_location_urls(city_urls):
    locations = []

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(get_locations_in_city, url) for url in city_urls]
        for result in as_completed(futures):
            locations.extend(result.result())

    return locations


def get_locations_in_city(city_url, retry_count=0, reset_session=False):
    try:
        session = get_session(reset_session)
        r = session.get(city_url, headers=headers)

        soup = BeautifulSoup(r.text)
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
        logger.error(e)
        if retry_count < 3:
            return get_locations_in_city(city_url, retry_count + 1, True)
        else:
            return []


MISSING = "<MISSING>"


def get_country_code(country):
    if country == "United States":
        return "US"
    elif country == "Canada":
        return "CA"
    else:
        return MISSING


def get_hours(hours):
    if not hours or not len(hours):
        return MISSING
    return ",".join(hours)


def get(location, key):
    return location.get(key, MISSING) or MISSING


def get_location(loc, retry_count=0, reset_session=False):
    locator_domain = "uhaul.com"
    page_url = loc.get("url")
    store_number = loc.get("entityNum")
    location_type = "<MISSING>"
    lat = loc.get("lat")
    lng = loc.get("long")

    try:
        session = get_session(reset_session)
        r = session.get(page_url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text)
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
        street_address = address.get("streetAddress").strip()
        city = address.get("addressLocality")
        state = address.get("addressRegion")
        postal = address.get("postalCode")
        country_code = get_country_code(address.get("addressCountry"))
        phone = get(data, "telephone")
        hours = get_hours(data.get("openingHours"))

        return [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            lat,
            lng,
            hours,
        ]

    except Exception as e:
        logger.error(e)
        if retry_count < 3:
            return get_location(loc, retry_count + 1, True)
        else:
            return []


def fetch_data():
    states = get_state_urls()
    cities = get_city_urls(states)
    locs = get_location_urls(cities)

    logger.info(f"number of locations: {len(locs)}")

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_location, loc) for loc in locs]
        for result in as_completed(futures):
            record = result.result()
            if record:
                yield record


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
