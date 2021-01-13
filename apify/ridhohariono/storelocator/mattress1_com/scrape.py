import re
import json
import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "mattress1.com"
BASE_URL = "https://www.mattress1.com/"
LOCATION_URL = "https://www.mattress1.com/storelocator"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def write_output(data):
    log.info("Write Output of " + DOMAIN)
    with open("data.csv", mode="w") as output_file:
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


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def get_hours(page_url):
    hours = []
    soup = pull_content(page_url)
    content = soup.find("div", {"id": "open_hour"})
    hours = content.find("table").get_text(strip=True, separator=",")
    return hours


def parse_json(link_url, js_variable):
    soup = pull_content(link_url)
    pattern = re.compile(
        r"var\s+" + js_variable + "\\s*=\\s*(\\{.*?\\});", re.MULTILINE | re.DOTALL
    )
    script = soup.find("script", text=pattern)
    if not script:
        return False
    parse = re.search(r"stores.*\[(\{.*?\})\]", script.string)
    if parse:
        data = json.loads("[{}]".format(parse.group(1)))
    else:
        return False
    return data


def fetch_data():
    store_info = parse_json(LOCATION_URL, "storeTranslate")
    locations = []
    for row in store_info:
        page_url = BASE_URL + row["rewrite_request_path"]
        location_name = handle_missing(row["name"])
        street_address = handle_missing(row["address"])
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zipcode"])
        country_code = handle_missing(row["country"])
        store_number = row["storelocator_id"]
        phone = handle_missing(row["phone"])
        location_type = handle_missing("<MISSING>")
        latitude = handle_missing(row["latitude"])
        longitude = handle_missing(row["longtitude"])
        hours_of_operation = handle_missing(get_hours(page_url))
        locations.append(
            [
                DOMAIN,
                page_url,
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
        )
    return locations


def scrape():
    log.info("Start {} Scraper".format(DOMAIN))
    data = fetch_data()
    log.info("Found {} locations".format(len(data)))
    write_output(data)
    log.info("Finish processed " + str(len(data)))


scrape()
