import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re
import json

DOMAIN = "blairsmarket.com"
BASE_URL = "https://www.blairsmarket.com/"
API_URL = "https://afsshareportal.com/lookUpFeatures.php?action=storeInfo&website_url=blairsmarket.com"

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
    return field.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    req = session.get(API_URL, headers=HEADERS)
    store_lists = json.loads(re.sub(r"([a-zA-Z_0-9\.]*\()|(\);?$)", "", req.text))
    locations = []
    for row in store_lists:
        page_url = BASE_URL + row["store_name"].replace("Blair's ", "").lower()
        locator_domain = DOMAIN
        location_name = row["store_name"]
        street_address = handle_missing(row["store_address"])
        city = handle_missing(row["store_city"])
        state = handle_missing(row["store_state"])
        zip_code = handle_missing(row["store_zip"])
        phone = handle_missing(row["store_phone"])
        hours_of_operation = (
            "Monday-Sat: "
            + row["store_hMonOpen"]
            + " - "
            + row["store_hMonClose"]
            + ", Sunday: "
            + row["store_hSunOpen"]
            + " - "
            + row["store_hSunClose"]
        )
        country_code = "US"
        store_number = row["store_id"]
        location_type = "blairsmarket"
        latitude = handle_missing(row["store_lat"])
        longitude = handle_missing(row["store_lng"])
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                locator_domain,
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
