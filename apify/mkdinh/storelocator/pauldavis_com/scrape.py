import csv
import time
import datetime
import re
import threading
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

MISSING = "<MISSING>"
max_workers = 10
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}
thread_local = threading.local()


def get_or_default(obj, key):
    val = obj.get(key, MISSING)
    return val if val else MISSING


def write_output(data):
    with open("data.csv", "w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "store_number",
                "location_type",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "latitude",
                "longitude",
                "phone",
                "hours_of_operation",
            ]
        )

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def get_session(reset=False):
    if not hasattr(thread_local, "session") or (reset == True):
        thread_local.session = SgRequests()
    return thread_local.session


def create_url(url):
    return f"https://pauldavis.com{url}"


def parse_location_urls(urls):
    return [url.get("href") for url in urls if "paul-davis-location" in url.get("href")]


def fetch_state_urls():
    states_url = "https://pauldavis.com/paul-davis-locations/"
    r = session.get(states_url)
    bs = BeautifulSoup(r.text, "html.parser")
    urls = bs.select(".content .cell a")
    return parse_location_urls(urls)


def fetch_cities(url):
    r = session.get(create_url(url))
    bs = BeautifulSoup(r.text, "html.parser")
    urls = bs.select(".content a")
    return parse_location_urls(urls)


def enqueue_cities(urls):
    links = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_cities, url) for url in urls]

        for job in as_completed(futures):
            data = job.result()
            links.extend(data)

    return links


def create_location(component):
    name = component.text

    href = component.get("href")
    url = href if "https://" in href else f"https://{href}"

    return {"name": name, "url": url}


def fetch_locations(url):
    r = session.get(create_url(url))
    bs = BeautifulSoup(r.text, "html.parser")
    urls = bs.select(".content a")
    return [create_location(url) for url in urls if ".pauldavis.com" in url.get("href")]


def enqueue_locations(urls):
    location_map = {}
    links = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_locations, url) for url in urls]

        for job in as_completed(futures):
            locations = job.result()
            for location in locations:
                url = location.get("url")
                if not location_map.get(url):
                    location_map[url] = True
                    links.append(location)

    return links


def get_alt_info(bs):
    info = [
        x
        for x in bs.select_one('[itemprop="articleBody"] p:last-of-type')
        .getText()
        .split("\n")
    ]

    if len(info) < 5:
        info.insert(0, None)
        info.insert(0, None)

    street_address = info[1]
    city_state_zipcode = info[2]
    phone = info[3]

    city, state_zipcode = city_state_zipcode.split(", ")
    state, *rest = re.split("\.?\s", state_zipcode)
    zipcode = rest[0] if len(rest) > 0 else None

    return {
        "street_address": street_address,
        "city": city,
        "state": state,
        "zipcode": zipcode,
        "phone": phone,
    }


def fetch_location_data(location):
    locator_domain = "pauldavis.com"
    page_url = location.get("url")
    location_name = location.get("name")

    r = get_session().get(page_url)
    bs = BeautifulSoup(r.text, "html.parser")

    info = {}

    address = bs.select("address .info")
    city_state_zipcode = address[1].getText().split(", ")

    city = city_state_zipcode.pop(0)
    state_zipcode = city_state_zipcode.pop()

    state, zipcode = re.split("\.?\s", state_zipcode)

    info["street_address"] = address[0].getText()
    info["city"] = city
    info["state"] = state
    info["zipcode"] = zipcode
    info["country_code"] = "US"

    if not info["street_address"]:
        info["street_address"] = get_alt_info(bs)["street_address"]

    if not info["city"]:
        info["city"] = get_alt_info(bs)["city"]

    if not info["state"]:
        info["state"] = get_alt_info(bs)["state"]

    if not info["zipcode"]:
        info["zipcode"] = get_alt_info(bs)["zipcode"]

    phones = re.split("[\/|\|or]\s", bs.select_one(".phone-icon").getText())
    cleaned_phone = [re.sub("\D", "", phone) for phone in phones]
    info["phone"] = "|".join(cleaned_phone)

    store_number = MISSING
    location_type = MISSING
    latitude = MISSING
    longitude = MISSING
    hours_of_operation = MISSING

    return [
        locator_domain,
        page_url,
        get_or_default(info, "location_name"),
        store_number,
        location_type,
        get_or_default(info, "street_address"),
        get_or_default(info, "city"),
        get_or_default(info, "state"),
        get_or_default(info, "zipcode"),
        get_or_default(info, "country_code"),
        latitude,
        longitude,
        get_or_default(info, "phone"),
        hours_of_operation,
    ]


def enqueue_locations_data(locations):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(fetch_location_data, location) for location in locations
        ]

        for job in as_completed(futures):
            data = job.result()
            yield data


def fetch_data():
    state_urls = fetch_state_urls()
    print(f"states count: {len(state_urls)}")

    city_urls = enqueue_cities(state_urls)
    print(f"cities count: {len(city_urls)}")

    location_urls = enqueue_locations(city_urls)
    print(f"locations count: {len(location_urls)}")

    yield from enqueue_locations_data(location_urls)


def scrape():
    print("-------------")

    start = time.time()

    data = fetch_data()
    write_output(data)

    end = time.time()

    elapsed = end - start
    print("-------------")
    print(f"duration: {datetime.timedelta(seconds=elapsed)}")
    print("-------------")


scrape()
