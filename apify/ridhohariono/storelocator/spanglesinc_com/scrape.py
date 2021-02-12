import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "spanglesinc.com"
BASE_URL = "https://www.spanglesinc.com"
LOCATION_URL = "https://www.spanglesinc.com/locations"
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
    store_content = soup.find("ul", {"id": "location-results"}).find_all("li")
    locations = []
    for row in store_content:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = handle_missing(
            row.find("p", {"class": "result-name"}).text.strip()
        )
        street_address = handle_missing(
            row.find("p", {"class": "result-address"}).text.strip()
        )
        state_contact = row.find_all("p", {"class": "result-contact"})
        if len(state_contact) < 2:
            addr_detail = state_contact[0].text.split(",")
            city = addr_detail[0]
            state = re.sub(r"\d+", "", addr_detail[1]).strip()
            zip_code = re.sub(r"\D", "", addr_detail[1]).strip()
            phone = "<MISSING>"
        else:
            addr_detail = state_contact[0].text.split(",")
            city = addr_detail[0]
            state = re.sub(r"\d+", "", addr_detail[1]).strip()
            zip_code = re.sub(r"\D", "", addr_detail[1]).strip()
            phone = handle_missing(state_contact[1].text.strip())
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = row.find("div", {"id": "hoursTable"}).get_text(
            strip=True, separator=" "
        )
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
