import csv
import json
import re
import time
import random
import threading
import requests_random_user_agent  # noqa
from bs4 import BeautifulSoup
from sglogging import SgLogSetup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgzip.static import static_zipcode_list
from sgzip.dynamic import SearchableCountries

logger = SgLogSetup().get_logger("gnc_com")

show_logs = False
thread_local = threading.local()

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}

re_get_json = re.compile(
    r"map\.data\.addGeoJson\(\s*JSON\.parse\(\s*eqfeed_callback\((.+?)\)\s*\)\s*\);"
)


def sleep(min=2, max=10):
    duration = random.randint(min, max)
    time.sleep(duration)


def log(*args, **kwargs):
    if show_logs:
        logger.info(" ".join(map(str, args)), **kwargs)


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
    # give each thread its own session object.
    # when using proxy, each thread's session will have a unique IP, and we'll switch IPs every 10 requests
    if (
        (not hasattr(thread_local, "session"))
        or (hasattr(thread_local, "request_count") and thread_local.request_count == 10)
        or reset
    ):
        thread_local.session = SgRequests()
        # print out what the new IP is ...
        if show_logs:
            r = thread_local.session.get("https://jsonip.com/")
            log(
                f"new IP for thread id {threading.current_thread().ident}: {r.json()['ip']}"
            )

    if hasattr(thread_local, "request_count") and thread_local.request_count == 10:
        reset_request_count()

    return thread_local.session


def reset_request_count():
    if hasattr(thread_local, "request_count"):
        thread_local.request_count = 0


def increment_request_count():
    if not hasattr(thread_local, "request_count"):
        thread_local.request_count = 1
    else:
        thread_local.request_count += 1


def get_json_data(html):
    match = re.search(re_get_json, html)
    if not match:
        return None
    json_text = match.group(1)
    return json.loads(json_text)


def get_phone(soup):
    phone = soup.find("a", class_="store-phone")

    return re.sub("(|)", "", phone.getText()) or "<MISSING>" if phone else "<MISSING>"


def extract_hours(node):
    return node.getText().strip().replace("\n", " ")


def get_hours(soup):
    storeHours = soup.find("div", class_="storeLocatorHours")
    if not storeHours:
        return "<MISSING>"

    openingHours = storeHours.findChildren("span")
    return ",".join(extract_hours(day) for day in openingHours)


def search_zip(postal, reset=False, retry_count=0):
    log("searching: ", postal)
    url = "https://www.gnc.com/on/demandware.store/Sites-GNC2-Site/default/Stores-FindStores"
    payload = {
        "dwfrm_storelocator_countryCode": "US",
        "dwfrm_storelocator_distanceUnit": "mi",
        "dwfrm_storelocator_postalCode": postal,
        "dwfrm_storelocator_maxdistance": "100",
        "dwfrm_storelocator_findbyzip": "Search",
    }
    session = get_session(reset=reset)
    # get the home page before each search to avoid captcha
    session.get("https://www.gnc.com/", headers=headers, timeout=1)
    sleep()
    try:
        r = session.post(url, headers=headers, data=payload)
        r.raise_for_status()
        increment_request_count()
        data = get_json_data(r.text)
        if data:
            return data.get('features', [])
        else:
            return []
    except Exception as ex:
        if retry_count < 3:
            return search_zip(postal, True, retry_count + 1)
        logger.info(f">>> exception searching zip {postal} >>> {ex}")


def get_location(loc, reset_session=False, retry_count=0):
    props = loc["properties"]
    store_id = props["storenumber"]
    website = "gnc.com"
    typ = "<MISSING>"
    name = props["title"]
    url = "https://www.gnc.com/store-details?StoreID=" + store_id
    addr = props["address1"]
    if props["address2"] is not None:
        addr = addr + ", " + props["address2"]
    addr = addr.strip() if addr else "<MISSING>"
    city = props["city"].strip()
    state = props["state"]
    zc = props["postalCode"]
    lat = loc["geometry"]["coordinates"][1]
    lng = loc["geometry"]["coordinates"][0]
    country = "US"
    try:
        session = get_session(reset=reset_session)
        sleep()
        r = session.get(url, headers=headers)
        r.raise_for_status()
        increment_request_count()

        soup = BeautifulSoup(r.text, "html.parser")
        phone = get_phone(soup)
        hours = get_hours(soup)

        location = [
            website,
            url,
            name,
            addr,
            city,
            state,
            zc,
            country,
            store_id,
            phone,
            typ,
            lat,
            lng,
            hours,
        ]
        return [x if x else "<MISSING>" for x in location]

    except Exception as ex:
        if retry_count < 3:
            return get_location(loc, True, retry_count + 1)
        logger.info(f">>> exception getting location {loc} >>> {ex}")


def fetch_data():
    store_ids = []
    zip_searched = 0
    zips = static_zipcode_list(50, SearchableCountries.USA)
    search_results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(search_zip, zipcode) for zipcode in zips]
        for result in as_completed(futures):
            locations = result.result()
            zip_searched += 1
            logger.info(f'pulling: {len(locations)} | found: {len(search_results)} | zipcodes: {zip_searched}/{len(zips)}')
            for loc in locations:
                store_id = loc["properties"]["storenumber"]
                if store_id not in store_ids:
                    search_results.append(loc)
                    store_ids.append(store_id)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_location, result) for result in search_results]
        for result in as_completed(futures):
            loc = result.result()
            if loc is not None:
                yield loc


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
