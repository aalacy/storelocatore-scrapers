import json
import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "countrykitchenrestaurants.com"
BASE_URL = "https://countrykitchenrestaurants.com"
LOCATION_URL = "https://countrykitchenrestaurants.com/locations/"
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


def parse_json(link_url, js_variable):
    soup = pull_content(link_url)
    pattern = re.compile(r"var\s+" + js_variable + r"\s+=\s+", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    if not script:
        return False
    parse = re.search(r'(?s)\(\{"map_options":\{.*\}\)', script.string)
    place = re.search(r'(?s)"places":(\[\{.*?\}\]),"listing"', parse.group())
    data = json.loads(place.group(1))
    return data


def get_hours(link_url):
    soup = pull_content(link_url)
    content = soup.find("div", {"class": "location-hours"})
    hoo = content.find("p").get_text(strip=True, separator=",")
    return hoo


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    store_info = parse_json(LOCATION_URL, "map1")
    locations = []
    for row in store_info:
        content = bs(row["content"], "lxml")
        page_url = content.find("a")["href"]
        if DOMAIN not in page_url:
            page_url = BASE_URL + page_url
        location_name = row["title"]
        street_address = handle_missing(row["address"])
        location = row["location"]
        city = handle_missing(location["city"])
        state = handle_missing(location["state"])
        zip_code = handle_missing(location["postal_code"])
        if location["country"] == "USA" or location["country"] == "United States":
            country_code = "US"
        elif location["country"] == "CA" or location["country"] == "CAN":
            country_code = "CA"
        elif location["country"] == "UK" or location["country"] == "United Kingdom":
            country_code = "UK"
        else:
            country_code = location["country"]
        store_number = row["id"]
        phone = handle_missing(bs(location["extra_fields"]["phone"], "lxml").text)
        location_type = "<MISSING>"
        latitude = handle_missing(location["lat"])
        longitude = handle_missing(location["lng"])
        hours_of_operation = get_hours(page_url)
        log.info("Append {} => {}".format(location_name, street_address))
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
