import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re
from helper import global_zip_code


DOMAIN = "bestseller.com"
BASE_URL = "https://about.bestseller.com/"
LOCATION_URL = "https://about.bestseller.com/our-brands/vila#stores"
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
    soup = pull_content(LOCATION_URL)
    ul_list = soup.find("div", {"id": "stores"}).find_all(
        "ul", {"class": re.compile(r"list-items office-list toggle-content.*")}
    )
    locations = []
    for ul in ul_list:
        list = ul.find_all("li")
        for row in list:
            page_url = LOCATION_URL
            locator_domain = DOMAIN
            location_name = row.find("b", {"class": "office-title"}).text.strip()
            addresess = (
                re.sub(
                    r"\|\S*@\S*\s?",
                    "",
                    row.find("p", {"class": "office-address"}).get_text(
                        strip=True, separator="|"
                    ),
                )
                .replace("|Get ", "")
                .replace("directions", "")
                .split("|")
            )
            street_address = handle_missing(addresess[0])
            city_zip = addresess[1].split()
            country_code = ul.find_parent("div").find("label").text.strip()
            zip_code = global_zip_code(country_code, addresess[1])
            if not zip_code:
                city = handle_missing(city_zip[-1])
                zip_code = handle_missing(addresess[1].replace(city, ""))
            else:
                city = handle_missing(addresess[1].replace(zip_code, ""))
            state = "<MISSING>"
            if "Dublin" in addresess[1]:
                state = "Dublin 1"
            phone = handle_missing(addresess[2]) if len(addresess) > 2 else "<MISSING>"
            hours_of_operation = "<MISSING>"
            store_number = "<MISSING>"
            location_type = "BRAND"
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
