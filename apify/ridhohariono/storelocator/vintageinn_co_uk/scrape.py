import csv
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "vintageinn.co.uk"
BASE_URL = "https://vintageinn.co.uk"
LOCATION_URL = "https://www.vintageinn.co.uk/cborms/pub/brands/8/outlets"
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


def get_hours(store_id):
    url = "{}/{}".format(LOCATION_URL, store_id)
    detail = session.get(url, headers=HEADERS).json()
    hours = []
    for x in detail["foodServiceTimes"]["periods"]:
        parse_hours = "{}: {}".format(x["days"]["text"], x["times"][0]["text"])
        hours.append(parse_hours)
    return ", ".join(hours)


def fetch_data():
    log.info("Fetching store_locator data")
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info:
        page_url = "https://www.vintageinn.co.uk/restaurants"
        locator_domain = DOMAIN
        location_name = handle_missing(row["name"])
        address = row["address"]
        if "line2" in address:
            street_address = "{}, {}".format(address["line1"], address["line2"])
        else:
            street_address = address["line1"]
        city = handle_missing(address["town"])
        state = address["county"] if "county" in address else "UK"
        zip_code = handle_missing(address["postcode"])
        country_code = handle_missing(address["country"])
        store_number = handle_missing(row["bunCode"])
        phone = handle_missing(row["telephoneNumber"])
        location_type = handle_missing(row["status"])
        latitude = handle_missing(row["gpsCoordinates"]["latitude"])
        longitude = handle_missing(row["gpsCoordinates"]["longitude"])
        hours_of_operation = handle_missing(get_hours(row["bunCode"]))
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
