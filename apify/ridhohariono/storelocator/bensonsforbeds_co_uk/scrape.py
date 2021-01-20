import csv
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "bensonsforbeds.co.uk"
BASE_URL = "https://bensonsforbeds.co.uk"
LOCATION_URL = "https://storerocket.global.ssl.fastly.net/api/user/jN64K6KpgV/locations"
HEADERS = {
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
    log.info("Fetching store_locator data")
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info["results"]["locations"]:
        page_url = "https://www.bensonsforbeds.co.uk/store-finder/"
        locator_domain = DOMAIN
        location_name = handle_missing(row["name"])
        if row["address_line_2"] and len(row["address_line_2"]) > 0:
            street_address = "{}, {}".format(
                row["address_line_1"], row["address_line_2"]
            )
        else:
            street_address = row["address_line_1"]
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["postcode"])
        country_code = handle_missing(row["country"])
        store_number = handle_missing(row["id"])
        phone = handle_missing(row["phone"])
        location_type = "<MISSING>"
        latitude = handle_missing(row["lat"])
        longitude = handle_missing(row["lng"])
        hours_of_operation = "<INACCESSIBLE>"
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
