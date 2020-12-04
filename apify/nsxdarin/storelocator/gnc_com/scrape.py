import csv
from sgrequests import SgRequests
import requests_random_user_agent  # noqa
import json
import re
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from sglogging import SgLogSetup

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
re_get_phone = re.compile(r'<a href="tel:(.+?)" class="store-phone">')
re_get_hours_section = re.compile(r'<div class="storeLocatorHours">([\s\S]+?)<\/div>')
re_get_hours_days = re.compile(r"<span><span>([\s\S]+?)<\/span>([\s\S]+?)<\/span>")


def sleep(min=2, max=10):
    duration = random.randint(min, max)
    # log('sleeping ', duration)
    time.sleep(duration)


def log(*args, **kwargs):
    if show_logs == True:
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
        or (reset == True)
    ):
        thread_local.session = SgRequests()
        # print out what the new IP is ...
        if show_logs == True:
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
    json_text = match.group(1)
    return json.loads(json_text)


def get_phone(html):
    match = re.search(re_get_phone, html)
    if match is None:
        return "<MISSING>"
    else:
        return match.group(1)


def get_hours(html):
    match_section = re.search(re_get_hours_section, html)
    if match_section is None:
        return "<MISSING>"

    hours = ""
    match_days = re.findall(re_get_hours_days, match_section.group(1))
    if len(match_days) == 0:
        return "<MISSING>"

    for m in match_days:
        if len(hours) > 0:
            hours = hours + ", "
        hours = f"{hours}{m[0].strip()}: {m[1].strip()}"

    hours = hours.replace("\n", "")
    return hours


def search_zip(postal, reset=False, attempts=1):
    log("searching: ", postal)
    url = "https://www.gnc.com/on/demandware.store/Sites-GNC2-Site/default/Stores-FindStores"
    payload = {
        "dwfrm_storelocator_countryCode": "US",
        "dwfrm_storelocator_distanceUnit": "mi",
        "dwfrm_storelocator_postalCode": postal,
        "dwfrm_storelocator_maxdistance": "15",
        "dwfrm_storelocator_findbyzip": "Search",
    }
    session = get_session(reset=reset)
    # get the home page before each search to avoid captcha
    session.get("https://www.gnc.com/", headers=headers)
    sleep()
    try:
        r = session.post(url, headers=headers, data=payload)
        r.raise_for_status()
        increment_request_count()
        return get_json_data(r.text)["features"]
    except Exception as ex:
        logger.info(f">>> exception searching zip {postal} >>> {ex}")


def get_location(loc, reset_session=False, attempts=1):
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
    session = get_session(reset=reset_session)
    sleep()
    try:
        r = session.get(url, headers=headers)
        r.raise_for_status()
        increment_request_count()
        phone = get_phone(r.text)
        hours = get_hours(r.text)

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
        logger.info(f">>> exception getting location {loc} >>> {ex}")


def fetch_data():
    store_ids = []
    zips = [
        "60007",
        "10002",
        "90210",
        "96795",
        "99515",
        "98115",
        "88901",
        "87101",
        "59715",
        "80014",
        "75001",
        "32034",
        "70032",
        "37011",
        "63101",
        "58102",
        "55408",
    ]
    search_results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(search_zip, zipcode) for zipcode in zips]
        done, not_done = wait(futures, return_when=ALL_COMPLETED)
        log(f"Done futures: {len(done)}")
        log(f"Not Done futures: {len(not_done)}")
        for result in futures:
            locations = result.result()
            for loc in locations:
                store_id = loc["properties"]["storenumber"]
                if store_id not in store_ids:
                    log(f"queuing store id: {store_id}")
                    search_results.append(loc)
                    store_ids.append(store_id)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_location, result) for result in search_results]
        wait(futures, return_when=ALL_COMPLETED)
        for result in futures:
            loc = result.result()
            if loc is not None:
                yield loc


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
