import csv
import re
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "barcelonawinebar.com"
BASE_URL = "https://www.barcelonawinebar.com"
LOCATION_URL = "https://barcelonawinebar.com/locations/"
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


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = []
    for val in soup.find_all(
        "a",
        href=re.compile(r"https\:\/\/barcelonawinebar.com\/location\/[a-zA-Z0-9_.-]"),
        title=True,
    ):
        content = val.find("div", {"class": "info-wrap-two"})
        city = content.find("h3").text.strip()
        state = val.find_parent("div", {"class": "state"})["id"]
        store_dict = {"link": val["href"], "city": city, "state": state}
        store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for row in store_urls:
        page_url = row["link"]
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        location_name = soup.find("meta", {"property": "og:title"})["content"]
        address = soup.find("address").get_text(strip=True, separator=",").split(",")
        parse_addr = usaddress.tag(", ".join(address))[0]
        street_address = address[0]
        city = parse_addr["PlaceName"] if "PlaceName" in parse_addr else row["city"]
        state = parse_addr["StateName"] if "StateName" in parse_addr else row["state"]
        zip_code = parse_addr["ZipCode"] if "ZipCode" in parse_addr else "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = handle_missing(
            soup.find("a", {"href": re.compile(r"tel:\d+")}).text.strip()
        )
        get_hoo = (
            soup.find("time")
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
        )
        hoo = []
        if "Temporarily Closed" not in get_hoo:
            location_type = "OPEN"
            for val in get_hoo.split(","):
                if re.match(r".*\:\s+\d{1,2}", val):
                    hoo.append(val)
            hours_of_operation = handle_missing(", ".join(hoo))
        else:
            location_type = "TEMP_CLOSED"
            hours_of_operation = "<MISSING>"
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
