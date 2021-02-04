import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import sglog

DOMAIN = "shopaplusrentals.com"
BASE_URL = "https://shopaplusrentals.com"
LOCATION_URL = "https://shopaplusrentals.com/api/v1/locations/"
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


def get_hours(link_url):
    soup = pull_content(link_url)
    content = soup.find("table", {"class": "table table-borderless"})
    hoo = content.get_text(strip=True, separator=",")
    return hoo.replace("day,", "day: ").replace("Online Only", "<MISSING>")


def fetch_data():
    store_info = session.post(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info["locations"]:
        page_url = BASE_URL + row["store_page"]
        location_name = handle_missing(row["name"])
        street_address = handle_missing(row["address"])
        city = handle_missing(row["city"])
        state = handle_missing(row["state"])
        zip_code = handle_missing(row["zipcode"])
        store_number = row["store_number"]
        phone = handle_missing(row["phone_number"])
        country_code = "US"
        latitude = handle_missing(row["latitude"])
        longitude = handle_missing(row["longitude"])
        hours_of_operation = get_hours(page_url)
        if hours_of_operation == "<MISSING>":
            street_address = "<MISSING>"
            location_type = "ONLINE_ONLY"
        else:
            location_type = "<MISSING>"
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
