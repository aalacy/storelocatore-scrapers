import re
import csv
import json
import time
import random
import threading
from urllib.parse import urljoin
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


def get_session():
    if (
        not hasattr(thread_local, "session")
        or thread_local.request_count > 5
        or thread_local.session_failed
    ):
        thread_local.session = SgRequests()
        thread_local.request_count = 0
        thread_local.session_failed = False

    thread_local.request_count += 1
    return thread_local.session


def mark_session_failed():
    thread_local.session_failed = True


def is_valid(soup):
    is_valid = soup.select_one("#header") or soup.select_one(".pharmacy-logo")
    if not is_valid:
        mark_session_failed()

    return is_valid


@retry(reraise=True, stop=stop_after_attempt(5))
def enqueue_links(url, selector):
    urls = []
    get_session()
    r = session.get(url, headers=headers)
    if r.status_code != 200:
        r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    if not is_valid(soup):
        raise Exception(f"Unable to extract data from {url}")

    links = soup.select(selector)

    for link in links:
        lurl = urljoin(base_url, link["href"])
        urls.append(lurl)

    return urls


def scrape_state_urls(state_urls):
    city_urls = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(enqueue_links, url, ".states a") for url in state_urls
        ]
        for future in as_completed(futures):
            urls = future.result()
            city_urls.extend(urls)

    return city_urls


def scrape_city_urls(city_urls):
    # scrape each city url and populate loc_urls with the results
    loc_urls = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(enqueue_links, url, ".directions-link a")
            for url in city_urls
        ]
        for future in as_completed(futures):
            urls = future.result()
            loc_urls.extend(urls)

    return loc_urls


@retry(reraise=True, stop=stop_after_attempt(5))
def get_location(loc):
    session = get_session()
    r = session.get(loc, headers=headers)
    location = BeautifulSoup(r.text, "html.parser")

    if not is_valid(location):
        raise Exception(f"Unable to extract data from {loc}")

    script = location.select_one("#structured-data-block")
    if not script:
        raise Exception(f"Unable to extract data from {loc}")

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
        for future in as_completed(futures):
            try:
                record = future.result()
                if record:
                    yield record
            except Exception as e:
                logger.error(str(e))


def fetch_data():
    state_urls = enqueue_links(
        urljoin(base_url, "/store-locator/cvs-pharmacy-locations"), ".states a"
    )

    logger.info(f"number of states: {len(state_urls)}")
    city_urls = scrape_state_urls(state_urls)

    logger.info(f"number of cities: {len(city_urls)}")
    loc_urls = scrape_city_urls(city_urls)

    logger.info(f"number of locations: {len(loc_urls)}")
    return scrape_loc_urls(loc_urls)


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
