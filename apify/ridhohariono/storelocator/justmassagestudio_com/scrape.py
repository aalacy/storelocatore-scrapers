import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re

DOMAIN = "justmassagestudio.com"
BASE_URL = "https://justmassagestudio.com/"
LOCATION_URL = "https://justmassagestudio.com/"
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


def get_latlong(soup):
    pattern = re.compile(r"window\.wsb\[(.*)\]", re.MULTILINE | re.DOTALL)
    script = soup.find_all("script", text=pattern)
    if len(script) == 0:
        return False
    parse = re.search(
        r'"lat\\":\\"(-?\d+(\.\d+)?)\\",\\"lon\\":\\"\s*(-?\d+(\.\d+)?)\\"',
        script[3].string,
    )
    if not parse:
        parse = re.search(
            r'"lat\\":(-?\d+(\.\d+)?),\\"lon\\":\s*(-?\d+(\.\d+)?)', script[3].string
        )
    if not parse:
        return "<MISSING>", "<MISSING>"
    latitude = parse.group(1)
    longitude = parse.group(3)
    return latitude, longitude


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = [BASE_URL + "el-segundo", BASE_URL + "westchester"]
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        content = soup.find("div", {"data-aid": "CONTACT_INFO_CONTAINER_REND"})
        location_name = content.find("h4").text
        address = (
            content.find("p", {"data-aid": "CONTACT_INFO_ADDRESS_REND"})
            .get_text(strip=True, separator=",")
            .split(",")
        )
        street_address = handle_missing(address[0])
        city = handle_missing(address[1])
        state_zip = address[2].split()
        state = handle_missing(state_zip[0])
        zip_code = handle_missing(state_zip[1])
        phone = handle_missing(
            content.find("a", {"data-aid": "CONTACT_INFO_PHONE_REND"}).text
        )
        hours_of_operation = (
            content.find("div", {"data-aid": "CONTACT_HOURS_CUST_MSG_REND"})
            .get_text(strip=True, separator=",")
            .replace("EVERYDAY,", "EVERYDAY: ")
            .split(",")[0]
        )
        store_number = "<MISSING>"
        country_code = "US"
        location_type = "justmassagestudio"
        latitude, longitude = get_latlong(soup)
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
