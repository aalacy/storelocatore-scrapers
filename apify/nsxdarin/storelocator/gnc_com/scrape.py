import csv
import json
import re
import time
import random
import threading
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgzip.static import static_zipcode_list, SearchableCountries

logger = SgLogSetup().get_logger("gnc_com")
thread_local = threading.local()

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
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


def sleep(min=0, max=2):
    duration = random.randint(min, max)
    time.sleep(duration)


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(FIELDS)
        for rows in data:
            writer.writerows(rows)


def get_session():
    # give each thread its own session object.
    # when using proxy, each thread's session will have a unique IP, and we'll switch IPs every 6 requests
    if not hasattr(thread_local, "session") or thread_local.request_count > 3:
        thread_local.session = SgRequests(
            retry_behavior=None, proxy_rotation_failure_threshold=3
        )
        thread_local.request_count = 0

    return thread_local.session


def increment_request_count():
    thread_local.request_count += 1


def get_json_data(html):
    match = re.search(r"eqfeed_callback\((.+?)\)\s*\)\s*\)", html)
    if not match:
        return None
    json_text = match.group(1)
    return json.loads(json_text)


def get_phone(soup):
    phone = soup.find("a", class_="store-phone")
    return re.sub("(|)", "", phone.getText()) or MISSING if phone else MISSING


def extract_hours(node):
    return node.getText().strip().replace("\n", " ").replace("null", MISSING)


def get_hours(soup):
    storeHours = soup.find("div", class_="storeLocatorHours")
    if not storeHours:
        return MISSING

    openingHours = storeHours.find_all("span", recursive=False)
    hours_of_operation = [extract_hours(day) for day in openingHours]
    for hours in hours_of_operation:
        if MISSING not in hours:
            return ",".join(hours_of_operation)

    return MISSING


def find_node(entityNum, soup):
    link = soup.find("a", id=entityNum)
    node = link.find_parent("td")
    return node


def search_zip(postal, tracker):
    url = "https://www.gnc.com/on/demandware.store/Sites-GNC2-Site/default/Stores-FindStores"
    payload = {
        "dwfrm_storelocator_countryCode": "US",
        "dwfrm_storelocator_distanceUnit": "mi",
        "dwfrm_storelocator_postalCode": postal,
        "dwfrm_storelocator_maxdistance": "10",
        "dwfrm_storelocator_findbyzip": "Search",
    }
    try:
        with get_session() as session:
            # get the home page before each search to avoid captcha
            session.get("https://www.gnc.com/stores", headers=headers)
            sleep()
            res = session.post(url, data=payload, headers=headers)
            res.raise_for_status()

        data = get_json_data(res.text)
        locations = data.get("features", []) if data else []
        soup = BeautifulSoup(res.text, "html.parser")

        pois = []
        for location in locations:
            store_id = location["properties"]["storenumber"]
            if store_id in tracker:
                continue
            tracker.append(store_id)

            node = find_node(store_id, soup)
            location["properties"]["phone"] = get_phone(node)
            location["properties"]["hours"] = get_hours(node)
            pois.append(extract(location))

        return pois

    except Exception as e:
        logger.error(f"error fetching {postal} >>> {e}")
        return []


def get(obj, key):
    return obj.get(key, MISSING) or MISSING


def extract(loc):
    props = loc["properties"]
    locator_domain = "gnc.com"
    store_number = props["storenumber"]
    location_type = "<MISSING>"
    location_name = get(props, "title")
    page_url = f"https://www.gnc.com/store-details?StoreID={store_number}"

    street_address = get(props, "address1")
    if props["address2"]:
        street_address += f", {props['address2']}"
    street_address = street_address.strip() if street_address else MISSING

    city = get(props, "city").strip()
    state = get(props, "state")
    postal = get(props, "postalCode")
    country_code = "US"

    geometry = loc["geometry"]
    latitude = geometry["coordinates"][1]
    longitude = geometry["coordinates"][0]

    hours_of_operation = get(props, "hours")
    phone = get(props, "phone")

    location = {
        "locator_domain": locator_domain,
        "store_number": store_number,
        "location_type": location_type,
        "location_name": location_name,
        "page_url": page_url,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip": postal,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "phone": phone,
        "hours_of_operation": hours_of_operation,
    }

    return [location[field] for field in FIELDS]


def fetch_data():
    dedup_tracker = []
    zip_searched = 0
    zips = static_zipcode_list(10, SearchableCountries.USA)

    logger.info(f"total zips: {len(zips)}")

    with ThreadPoolExecutor() as executor:
        logger.info(f"initialize executor with {executor._max_workers} workers")
        futures = as_completed(
            [executor.submit(search_zip, zipcode, dedup_tracker) for zipcode in zips]
        )

        for future in futures:
            yield future.result()
            zip_searched += 1

            logger.info(
                f"found: {len(dedup_tracker)} | zipcodes: {zip_searched}/{len(zips)}"
            )


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
