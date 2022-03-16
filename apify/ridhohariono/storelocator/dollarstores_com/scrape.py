import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "dollarstores.com"
BASE_URL = "https://www.dollarstores.com/"
LOCATION_URL = "https://www.dollarstores.com/store-finder/"
API_URL = "https://www.dollarstores.com/wp-admin/admin-ajax.php?action=store_search&lat=48.42842&lng=-123.36564&max_results=2500&search_radius=500"

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
    store_lists = session.get(API_URL, headers=HEADERS).json()
    locations = []
    for row in store_lists:
        locator_domain = DOMAIN
        location_name = handle_missing(row["store"])
        street_address = handle_missing(row["address"] + row["address2"]).strip()
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zip"])
        phone = handle_missing(row["phone"])
        hours_of_operation = (
            bs(row["hours"], "lxml")
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
        )
        country_code = handle_missing(row["country"])
        store_number = row["id"]
        location_type = "dollarstores"
        latitude = handle_missing(row["lat"])
        longitude = handle_missing(row["lng"])
        log.info("Append {} => {}".format(location_name, street_address))
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
