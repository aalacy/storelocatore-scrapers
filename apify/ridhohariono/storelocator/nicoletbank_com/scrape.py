import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re


DOMAIN = "nicoletbank.com"
BASE_URL = "https://nicoletbank.com"
LOCATION_URL = "https://www.nicoletbank.com/branch-atm-locations"
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


def get_hoo(link):
    soup = pull_content(link)
    hoo = soup.find("div", {"class": "branch-hours"}).find_all("p")
    hoo = hoo[1].find("span")
    hours_of_operations = "{}: {}".format(hoo.text, hoo.next_sibling.strip())
    return hours_of_operations


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = (
        soup.find("div", {"class": "locator-branches"})
        .find("div", {"class": "branches"})
        .find("div", {"class": "branch-scroll"})
        .find_all("div", {"class": "branch clearfix"})
    )
    locations = []
    for row in content:
        page_url = BASE_URL + row.find("a", {"class": "branch-ico"})["href"]
        location_name = row["data-asodata1"].strip()
        street_address = handle_missing(row["data-asodata2"]).strip()
        city_state = row["data-asodata3"].split(",")
        city = handle_missing(city_state[0])
        state = (
            handle_missing(re.sub(r"\d+", "", city_state[1])).replace("-", "").strip()
        )
        zip_code = handle_missing(
            re.sub(r"\D+", "", city_state[1].split("-")[0])
        ).strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = row["data-info-address"].split("<br />")[1].strip()
        hours_of_operation = get_hoo(page_url)
        location_type = "nicoletbank"
        latitude = handle_missing(row["data-latitude"])
        longitude = handle_missing(row["data-longitude"])
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
