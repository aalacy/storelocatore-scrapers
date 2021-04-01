import csv
import re
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "arizonatile.com"
BASE_URL = "https://www.arizonatile.com/"
LOCATION_URL = "https://www.arizonatile.com/api/v1/locations"
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info:
        page_url = BASE_URL + row["url"]
        location_name = handle_missing(row["title"].strip())
        street_address = handle_missing(row["streetAddress"])
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zipcode"])
        country_code = "US"
        store_number = "<MISSING>"
        phone = handle_missing(row["primaryPhone"])
        if "Please contact Arizona Tile Sales Representative" in row["description"]:
            location_type = "ARIZONA TILE CONTACT"
        else:
            location_type = "ARIZONA TILE LOCATION"
        latitude = handle_missing(row["latitude"])
        longitude = handle_missing(row["longitude"])
        if row["serializableShowroomHours"]:
            hoo = ""
            for key, val in row["serializableShowroomHours"].items():
                hoo += key + val.replace(".", "") + ","
            hours_of_operation = re.sub(r",$", "", hoo)
        else:
            hours_of_operation = "<MISSING>"
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
