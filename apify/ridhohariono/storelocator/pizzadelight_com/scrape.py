import csv
import re
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "pizzadelight.com"
BASE_URL = "https://pizzadelight.com/"
LOCATION_URL = "https://www.pizzadelight.com/service/search/branch?page=all&lang=en"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(data):
    hoo = []
    for key, row in data.items():
        if not row["dining"]["range"] and not row["dining"]["range"]:
            return "<MISSING>"
        formated_hours = "{}: {} - {}".format(
            key, row["dining"]["range"][0]["from"], row["dining"]["range"][0]["to"]
        )
        hoo.append(formated_hours)
    return ", ".join(hoo)


def fetch_data():
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info:
        page_url = "https://www.pizzadelight.com/find-a-restaurant"
        location_name = handle_missing(row["title"])
        city = handle_missing(row["address"]["city"])
        street_address = handle_missing(row["address"]["address"])
        if "Marystown" not in street_address and "Cavendish" not in street_address:
            street_address = re.sub(city + ".*", "", street_address)
        street_address = re.sub(r"Hawke's Bay.*", "", street_address).strip()
        street_address = re.sub(r",$", "", street_address)
        state = handle_missing(row["address"]["province"])
        if state == "PEI":
            state = "Prince Edward Island"
        zip_code = handle_missing(row["address"]["zip"])
        country_code = "CA"
        store_number = row["id"]
        phone = handle_missing(row["phone"])
        if row["description"]:
            location_type = "OPEN"
            if "Coming soon" in row["description"]:
                location_type = "COMING_SOON"
            elif "Closed for" in row["description"]:
                location_type = "TEMP_CLOSED"
        latitude = handle_missing(row["lat"])
        longitude = handle_missing(row["lng"])
        hours_of_operation = parse_hours(row["schedule"]["week"])
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
