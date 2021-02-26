import re
import csv
import json
from bs4 import BeautifulSoup  # noqa
from sgrequests import SgRequests
from sglogging import SgLogSetup
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict

logger = SgLogSetup().get_logger("midas_com")


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


start_url = (
    "https://www.midas.com/partialglobalsearch/getstorelist?zipcode={}&language=en-us"
)
headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def get_state_urls(state_url, session):
    url = urljoin("https://midas.com", state_url)
    res = session.get(url)
    soup = BeautifulSoup(res.text, "lxml")

    store_regex = re.compile(r"\/store.aspx\?shopnum=\d+")
    stores = soup.find_all("a", href=store_regex)

    urls = [store["href"] for store in stores]
    return list(set(urls))


def get_location_urls(session, executor):
    urls = []
    res = session.get("https://www.midas.com/tabid/697/default.aspx")
    soup = BeautifulSoup(res.text, "lxml")

    us_ca_regex = re.compile(r"\/sitemap\.aspx\?country=(US|CA)", re.IGNORECASE)
    states = [a["href"] for a in soup.find_all("a", href=us_ca_regex)]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(get_state_urls, url, session) for url in states]
        for future in as_completed(futures):
            urls.extend(future.result())

    return urls


def get_location(url, session):
    page_url = urljoin("https://midas.com", url)

    query = parse_query(page_url)
    store_number = query["shopnum"]

    try:
        details = fetch_details(page_url, session)
        poi = fetch_poi(details, int(store_number), session)
        return extract(poi, details)
    except Exception as e:
        logger.error(e)


def parse_query(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    return {k: v[0].strip() for k, v in query.items()}


cached: Dict[int, dict] = {}  # noqa


def fetch_poi(details, store_number, session):
    address = details["address"]
    postal = get(address, "postalCode")
    cached_store = cached.get(store_number)
    if cached_store:
        return cached_store

    stores = session.get(start_url.format(postal), headers=headers).json()
    for store in stores:
        store_number = store["ShopNumber"]
        cached[store_number] = store

    return cached[store_number]


def fetch_details(url, session):
    res = session.get(url)
    soup = BeautifulSoup(res.text, "lxml")
    script = soup.find("script", {"type": "application/ld+json"})

    return json.loads(script.string)


MISSING = "<MISSING>"
DOMAIN = "midas.com"


def get(entity, key):
    return entity.get(key, MISSING) or MISSING


def extract(poi, details):
    store_number = poi["ShopNumber"]
    store_url = urljoin(start_url, get(poi, "ShopDetailsLink"))
    location_name = get(poi, "Name")
    street_address = get(poi, "Address")
    city = get(poi, "City")
    state = get(poi, "State")
    zip_code = get(poi, "ZipCode")
    country_code = get(poi, "Country")
    if re.search("canada", country_code, re.IGNORECASE):
        country_code = "CA"

    phone = get(poi, "PhoneNumber")
    latitude = get(poi, "Latitude")
    longitude = get(poi, "Longitude")

    location_type = get(details, "@type")
    hours_of_operation = get(details, "openingHours")

    return [
        DOMAIN,
        store_url,
        location_name,
        street_address,
        city,
        state,
        zip_code,
        country_code,
        store_number,
        phone,
        location_type,
        latitude,
        longitude,
        hours_of_operation,
    ]


def fetch_data():
    # Your scraper here
    session = SgRequests().requests_retry_session(retries=0)
    with ThreadPoolExecutor() as executor:
        urls = get_location_urls(session, executor)

        futures = [executor.submit(get_location, url, session) for url in urls]
        for future in as_completed(futures):
            yield future.result()


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
