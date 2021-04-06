import re
import csv
import json
import time
import random
import threading
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from sglogging import SgLogSetup
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("cvs_com")


start_time = datetime.now()

thread_local = threading.local()
base_url = "https://www.cvs.com"

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "connection": "Keep-Alive",
}


def sleep(min=3, max=3):
    duration = random.randint(min, max)
    time.sleep(duration)


def clean_hours(hour):
    cleaned = hour.text.strip().replace("\n", " ").replace("\t", "")
    return re.sub(r"\s\s+", " ", cleaned)


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
                "location_type",
                "store_number",
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
        for row in data:
            writer.writerow(row)

    end_time = datetime.now()
    timedelta = end_time - start_time
    logger.info("--------------------")
    duration = time.strftime("%H:%M:%S", time.gmtime(timedelta.total_seconds()))
    logger.info(f"duration: {duration}")


def get_session(reset=False):
    if not hasattr(thread_local, "session") or reset:
        thread_local.session = SgRequests()
    return thread_local.session


@retry(stop=stop_after_attempt(3))
def enqueue_links(url, selector):
    locs = []
    cities = []
    states = []

    get_session()
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select(selector)

    for link in links:
        lurl = f"{base_url}{link['href']}"
        path_count = lurl.count("/")
        if path_count == 5:
            states.append(lurl)
        elif path_count == 6:
            if "cvs-pharmacy-address" in lurl:
                locs.append(lurl)
            else:
                cities.append(lurl)
        else:
            raise Exception(f"invalid link: {lurl}")

    return {"locs": locs, "cities": cities, "states": states}


def scrape_state_urls(state_urls, city_urls):
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(enqueue_links, url, ".states a") for url in state_urls
        ]
        for result in as_completed(futures):
            urls = result.result()
            city_urls.extend(urls["cities"])


def scrape_city_urls(city_urls, loc_urls):
    # scrape each city url and populate loc_urls with the results
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(enqueue_links, url, ".directions-link a")
            for url in city_urls
        ]
        for result in as_completed(futures):
            d = result.result()
            loc_urls.extend(d["locs"])


@retry(stop=stop_after_attempt(3))
def get_location(loc):
    logger.info(f"Pulling Location: {loc}")

    session = get_session()
    r = session.get(loc, headers=headers)
    location = BeautifulSoup(r.text, "html.parser")
    script = location.select_one("#structured-data-block")
    if not script:
        logger.info(f"Unable to fetch location: {loc}")
        return None

    structured_data = script.string

    info = json.loads(structured_data)[0]

    locator_domain = "cvs.com"
    page_url = loc
    location_name = info["name"]
    location_type = info["@type"]
    store_number = info["url"].split("/")[-1]
    street_address = info["address"]["streetAddress"]
    city = info["address"]["addressLocality"]
    state = info["address"]["addressRegion"]
    zipcode = info["address"]["postalCode"]
    country_code = info["address"]["addressCountry"]
    latitude = (
        info["geo"]["latitude"] if info["geo"]["latitude"] != "0.0" else "<MISSING>"
    )
    longitude = (
        info["geo"]["longitude"] if info["geo"]["longitude"] != "0.0" else "<MISSING>"
    )
    phone = info["address"]["telephone"]

    hours = (
        location.select(".phHours li")
        if len(location.select(".phHours li"))
        else location.select(".srHours li")
    )

    hours_of_operation = ",".join([clean_hours(hour) for hour in hours])

    return [
        locator_domain,
        page_url,
        location_name,
        location_type,
        store_number,
        street_address,
        city,
        state,
        zipcode,
        country_code,
        latitude,
        longitude,
        phone,
        hours_of_operation,
    ]


def scrape_loc_urls(loc_urls):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_location, loc) for loc in loc_urls]
        for result in as_completed(futures):
            record = result.result()
            if record is not None:
                yield record


def fetch_data():
    urls = enqueue_links(
        f"{base_url}/store-locator/cvs-pharmacy-locations", ".states a"
    )

    state_urls = urls["states"]
    city_urls = urls["cities"]
    loc_urls = urls["locs"]

    logger.info(f"number of states: {len(state_urls)}")
    scrape_state_urls(state_urls, city_urls)

    logger.info(f"number of cities: {len(city_urls)}")
    scrape_city_urls(city_urls, loc_urls)

    with open("locations.json", "w") as file:
        json.dump(loc_urls, file)

    with open("locations.json") as file:
        loc_urls = json.load(file)

    logger.info(f"number of locations: {len(loc_urls)}")
    return scrape_loc_urls(loc_urls)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
