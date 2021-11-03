import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re


DOMAIN = "thepodhotel.com"
BASE_URL = "https://thepodhotel.com"
LOCATION_URL = "https://www.thepodhotel.com/contact-us.html"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = soup.find_all("table", {"class": "wsite-multicol-table"})
    locations = []
    for row in content:
        stores = row.find("tr", "wsite-multicol-tr").find_all(
            "div", {"class": "wsite-map"}
        )
        for store in stores:
            main = store.find_next("td")
            locator_domain = DOMAIN
            name = main.find("h2", {"class": "wsite-content-title"})
            if name:
                location_name = name.text.strip()
                info = name.find_next("div", {"class": "paragraph"})
                address = (
                    info.get_text(strip=True, separator=",")
                    .replace(",,", ",")
                    .split(",")
                )
                street_address = address[0].strip()
                city = address[1].strip()
                state = re.sub(r"\d+", "", address[2]).strip()
                zip_code = re.sub(r"\D+", "", address[2]).strip()
                country_code = "US"
                store_number = "<MISSING>"
                phone = info.find("a", href=re.compile(r"tel:.*"))["href"].replace(
                    "tel:", ""
                )
            hours_of_operation = "<MISSING>"
            location_type = "thepodhotel"
            latlong = store.find("iframe")["src"]
            latitude = re.search(r"lat\=(.*)\&domain", latlong).group(1)
            longitude = re.search(r"long\=(.*)\&lat", latlong).group(1)
            if is_multiple(location_name, locations):
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
