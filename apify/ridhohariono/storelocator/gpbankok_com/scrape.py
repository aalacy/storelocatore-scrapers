import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "gpbankok.com"
BASE_URL = "https://gpbankok.com"
LOCATION_URL = (
    "https://www.gpbankok.com/_/api/branches/35.4124659/-99.42981200000001/250"
)
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


def is_multiple(location_name, locations):
    for row in locations:
        if location_name in row:
            return False
    return True


def get_hoo(el):
    soup = bs(el, "lxml")
    hoo = soup.find("body").get_text(strip=True, separator=",").split(",")
    if len(hoo) > 1:
        hours_of_operations = "{}: {}".format(
            hoo[0].replace("Hours: ", "").strip(), hoo[1].replace("Lobby: ", "").strip()
        )
        return hours_of_operations
    return "<MISSING>"


def fetch_data():
    log.info("Fetching store_locator data")
    stores = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in stores["branches"]:
        location_name = row["name"]
        street_address = handle_missing(row["address"])
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zip"])
        country_code = "US"
        store_number = "<MISSING>"
        phone = row["phone"]
        hours_of_operation = "<MISSING>"
        if row["description"]:
            hours_of_operation = get_hoo(row["description"])
        location_type = "branch"
        latitude = handle_missing(row["lat"])
        longitude = handle_missing(row["long"])
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
                "https://www.gpbankok.com/about/locations",
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
