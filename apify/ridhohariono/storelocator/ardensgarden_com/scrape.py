import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "ardensgarden.com"
BASE_URL = "https://www.ardensgarden.com"
LOCATION_URL = "https://www.ardensgarden.com/pages/ardens-garden-stores"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"class": "twelve custom-store"}).find_all(
        "div", {"class": "row"}
    )[1]
    store_lists = content.find_all(
        "div", {"class": "panel panel-success panel-current-store center"}
    )
    locations = []
    for row in store_lists:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = row.find("h4", {"class": "store-title"}).text.strip()
        address = (
            row.find("div", {"class": "location-details"})
            .get_text(strip=True, separator="|")
            .split("|")
        )
        street_address = address[0].strip()
        city_state_zip = address[1].split(",")
        if len(city_state_zip) > 1:
            city = city_state_zip[0].strip()
            state = re.sub(r"\d+", "", city_state_zip[1]).strip()
            zip_code = re.sub(r"\D+", "", city_state_zip[1]).strip()
        else:
            city_state_zip = address[1].split(" ")
            city = city_state_zip[0].strip()
            state = city_state_zip[1]
            zip_code = city_state_zip[2]
        country_code = "US"
        store_number = "<MISSING>"
        phone = address[4]
        hours_of_operation = ", ".join(address[6:]).replace("to", "-")
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
