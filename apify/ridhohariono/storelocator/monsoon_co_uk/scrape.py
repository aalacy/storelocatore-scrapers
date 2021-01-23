import json
import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "monsoon.co.uk"
BASE_URL = "https://www.monsoon.co.uk"
LOCATION_URL = "https://www.monsoon.co.uk/stores/?country=GB"
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


def parse_hours(element, store_id):
    log.info("Parsing hours_of_operation => " + store_id)
    content = bs(element, "lxml")
    hours = content.get_text(strip=True, separator=",").replace("Opening hours:,", "")
    result = re.sub(r":,", ": ", hours)
    return result


def fetch_store_id():
    log.info("Fetching store ID")
    soup = pull_content(LOCATION_URL)
    content = soup.find(
        "ul", {"class": "b-tabs__content-container js-tabs__content-container"}
    )
    data = content.find(
        "li",
        {
            "class": "b-tabs__content b-storelocator__results js-tabs__content js-stores-list h-hidden"
        },
    )["data-stores"]
    return data


def fetch_store_data(store_id):
    endpoint = "https://www.monsoon.co.uk/on/demandware.store/Sites-monsoon-uk-Site/en_GB/Stores-FindStoreById?storeId={}&ajax=true"
    log.info("Fetching store Locatior by ID: " + store_id)
    info = session.get(endpoint.format(store_id), headers=HEADERS).json()
    return info


def fetch_data():
    log.info("Fetching store_locator data")
    store_ids = json.loads(fetch_store_id())
    skip_id = ["1387", "1274"]
    locations = []
    for row in store_ids:
        if row["ID"] in skip_id:
            continue
        data = fetch_store_data(row["ID"])
        store = data["store"]
        locator_domain = DOMAIN
        location_name = handle_missing(store["name"])
        if store["address2"] and len(store["address2"]) > 0:
            street_address = "{}, {}".format(store["address1"], store["address2"])
        else:
            street_address = handle_missing(store["address1"])
        city = handle_missing(store["city"])
        state = handle_missing(None if "stateCode" not in store else store["stateCode"])
        zip_code = handle_missing(store["postalCode"])
        country_code = handle_missing(store["countryCode"])
        store_number = row["ID"]
        phone = handle_missing(store["phoneFormatted"])
        hours_of_operation = parse_hours(store["workingHours"], row["ID"])
        sub_hoo = re.sub(r"[a-z]*:\s+", "", hours_of_operation, flags=re.IGNORECASE)
        if all(value == "CLOSED" for value in sub_hoo.split(",")):
            location_type = "TEMP_CLOSED"
        else:
            location_type = "OPEN"
        latitude = handle_missing(store["latitude"])
        longitude = handle_missing(store["longitude"])
        log.info(
            "Append info to locations => {}:{} => {}".format(
                latitude, longitude, street_address
            )
        )
        locations.append(
            [
                locator_domain,
                LOCATION_URL,
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
