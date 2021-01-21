import re
import csv
import threading
import usaddress
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgzip.static import (
    static_coordinate_list,
    SearchableCountries,
)

local = threading.local()
logger = SgLogSetup().get_logger("bobcat_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

MISSING = "<MISSING>"
FIELDS = [
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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


def get_session(reset=False):
    if not hasattr(local, "session") or reset or local.request_count == 3:
        local.session = SgRequests()
        local.request_count = 0

    return local.session


def get_location_name(tag):
    name_tag = tag.find("h4")
    if not name_tag:
        return MISSING

    return name_tag.getText().strip()


def parse_address(address):
    try:
        tokens, *others = usaddress.tag(address)
    except Exception:
        parsed = usaddress.parse(address)
        tokens = {}
        for value, label in parsed:
            if label not in tokens:
                tokens[label] = []
            tokens[label].append(value)

        for label in tokens:
            tokens[label] = " ".join(tokens[label])

    if not tokens.get("PlaceName"):
        fill_city(tokens, address)

    return tokens


def fill_city(tokens, address):
    normalized_tokens = [token.lower() for token in address.split(" ")]
    possible_name = (-1, None)
    for name in usaddress.STREET_NAMES:
        try:
            if name in normalized_tokens:
                idx = normalized_tokens.index(name)
                if idx > possible_name[0]:
                    possible_name = (idx, name)
        except Exception as e:
            print(e)

    idx, street_name = possible_name
    if street_name:
        try:
            street_address, city_and_others = re.split(street_name, address, flags=re.I)
            city, *others = city_and_others.split(", ")
            tokens["PlaceName"] = city.strip()
        except Exception as e:
            print(e)


def get_street_address(addr, address):
    street_address = address
    if addr.get("PlaceName"):
        street_address = street_address.replace(addr.get("PlaceName"), "")

    if addr.get("StateName"):
        street_address = street_address.replace(addr.get("StateName"), "")

    if addr.get("ZipCode"):
        street_address = street_address.replace(addr.get("ZipCode"), "")

    if addr.get("OccupancyIdentifier"):
        street_address = street_address.replace(addr.get("OccupancyIdentifier"), "")

    if addr.get("OccupancyType"):
        street_address = street_address.replace(addr.get("OccupancyType"), "")

    street_address = street_address.replace("Ave", "Avenue").replace(
        "Avenuenue", "Avenue"
    )

    street_address = re.sub(r"\s,", ",", street_address)
    street_address = street_address.strip()

    if street_address[-1] == ",":
        street_address = street_address[:-1]

    return street_address.strip()


def get_state_zip_country(addr, address):
    zipcode = addr.get("ZipCode") or addr.get("OccupancyIdentifier") or MISSING

    if zipcode.isdigit():
        state = addr.get("StateName") or MISSING
        return state, zipcode, "US"
    else:
        components = address.split(", ")
        if len(components) > 1:
            state_zip = components.pop()
            state, zipcode = state_zip.split(" ", 1)
            return state, zipcode, "CA"

    return MISSING, MISSING


def get_phone(tag):
    matched = re.search(r"(\d{3}\-\d{3}\-\d{4})", str(tag))
    if not matched:
        return MISSING

    return matched.group(1)


def get_page_url(tag):
    website_link = None
    for link in tag.find_all("a", class_="kw-result-link"):
        if re.search("website", link.getText(), re.I):
            website_link = link
            break

    if not website_link:
        return MISSING

    onclick = website_link["onclick"]
    if not onclick:
        return MISSING

    match = re.search(r"href=[\'|\"](.*)[\'|\"]", onclick)
    if not match:
        return MISSING

    return match.group(1)


def get_store_number(tag):
    onclick = tag["onclick"]
    if not onclick:
        return MISSING

    match = re.search(r"toggleDetail\([\'|\"](.*)[\'|\"],", onclick)
    if not match:
        return MISSING

    return match.group(1)


def fetch_us_location(coord, country, dedup_tracker, retry_count=0):

    lat, lng = coord
    url = "https://bobcat.know-where.com/bobcat/cgi/selection"
    params = {
        "place": "",
        "option": "",
        "lang": "en",
        "ll": f"{lat},{lng}",
        "stype": "ll",
        "async": "results",
    }

    session = get_session(retry_count > 0)
    try:
        res = session.get(url, params=params, headers=headers)
        local.request_count += 1
        res.raise_for_status()
    except Exception as e:
        if retry_count < 3:
            return fetch_us_location(coord, country, dedup_tracker, retry_count + 1)
        logger.error(f"unable to fetch coord: {lat} {lng} >>>> {e}")

    soup = BeautifulSoup(res.text, "lxml")
    locations = soup.find_all("td", class_="kw-results-info")

    data = []
    for location in locations:
        store_number = get_store_number(location)
        if store_number in dedup_tracker:
            continue
        dedup_tracker.append(store_number)

        address = location.find("span", onclick=True).getText().strip()
        addr = parse_address(address)
        if not addr:
            continue

        street_address = get_street_address(addr, address)
        city = addr.get("PlaceName") or MISSING
        state, zipcode, country_code = get_state_zip_country(addr, address)

        phone = get_phone(location)
        page_url = get_page_url(location)
        location_name = get_location_name(location)

        if " " in state:
            state = state.split(" ")[0]
            country_code = "CA"
        poi = {
            "locator_domain": "bobcat.com",
            "page_url": page_url,
            "location_name": location_name,
            "location_type": MISSING,
            "store_number": store_number,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip": zipcode,
            "country_code": country_code,
            "latitude": MISSING,
            "longitude": MISSING,
            "phone": phone,
            "hours_of_operation": MISSING,
        }
        data.append(poi)

    return data


def debounce_log_status(items_completed, items, dedup_tracker):
    if items_completed % 50 == 0 or items_completed == len(items):
        logger.info(
            f"status: {items_completed}/{len(items)} | locations found: {len(dedup_tracker)}"
        )


def fetch_locations(country_code, radius_miles, dedup_tracker):
    items_completed = 0
    country_locations_count = 0
    coords = static_coordinate_list(radius_miles, country_code)

    with ThreadPoolExecutor() as executor:
        logger.info(
            f"query {country_code.upper()} locations with {executor._max_workers} number of workers within {radius_miles} miles"
        )
        futures = [
            executor.submit(fetch_us_location, coord, country_code, dedup_tracker)
            for coord in coords
        ]
        for future in as_completed(futures):
            items_completed += 1
            debounce_log_status(items_completed, coords, dedup_tracker)

            for location in future.result():
                country_locations_count += 1
                yield [location[field] for field in FIELDS]

    logger.info(f"{country_code} locations: {country_locations_count}")


def fetch_data():
    dedup_tracker = []
    yield from fetch_locations(SearchableCountries.USA, 40, dedup_tracker)
    yield from fetch_locations(SearchableCountries.CANADA, 10, dedup_tracker)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
