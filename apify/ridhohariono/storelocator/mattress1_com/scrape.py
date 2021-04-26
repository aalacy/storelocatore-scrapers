import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "mattress1.com"
BASE_URL = "https://www.mattress1.com/"
LOCATION_URL = "https://mattress1.com/wp-admin/admin-ajax.php?action=store_search&lat=40.75797&lng=-73.98554&max_results=25&search_radius=50&autoload=1"
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


def get_hours(table):
    hours = []
    soup = bs(table, "lxml")
    hours = soup.find("table").get_text(strip=True, separator=",")
    result = hours.replace("day,", "day: ")
    return result


def fetch_data():
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info:
        page_url = row["permalink"]
        location_name = handle_missing(row["store"])
        if "address2" in row and len(row["address2"]) > 0:
            street_address = "{}, {}".format(row["address"], row["address2"])
        else:
            street_address = handle_missing(row["address"])
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zip"])
        country_code = "US"
        store_number = row["id"]
        phone = handle_missing(row["phone"])
        location_type = handle_missing("<MISSING>")
        latitude = handle_missing(row["lat"])
        longitude = handle_missing(row["lng"])
        hours_of_operation = handle_missing(get_hours(row["hours"]))
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
