import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "kidcarepediatrics.com"
BASE_URL = "https://kidcarepediatrics.com/"
LOCATION_URL = "https://kidcarepediatrics.com/locations/"
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
    store_urls = []
    soup = pull_content(LOCATION_URL)
    a_class = "btBtn btBtn btnFilledStyle btnAccentColor btnMedium btnNormalWidth btnRightPosition btnNoIcon"
    alinks = soup.find_all("a", {"class": a_class})
    for link in alinks:
        store_urls.append(link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def get_latlong(soup):
    script = soup.find(
        "script",
        text=re.compile(r"[a-zA-Z0-9]*bt_gmap_init.*", re.MULTILINE | re.DOTALL),
    )
    lat_long = (
        re.search(r"(-?[\d]*\.[\d]*),\s+(-?[\d]*\.[\d]*)", script.string)
        .group()
        .split(",")
    )
    return lat_long[0], lat_long[1]


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        location_name = (
            soup.find("title").text.strip().replace(" - Kid Care Pediatrics", "")
        )
        content = soup.find_all("div", {"class": "sTxt"})
        address = (
            content[0]
            .get_text(strip=True, separator=",")
            .replace("ADDRESS,", "")
            .split(",")
        )
        if len(address) > 3:
            street_address = ", ".join(address[:2])
            city = handle_missing(address[2])
            state_zip = address[3].strip().split(" ")
        else:
            street_address = handle_missing(address[0])
            city = handle_missing(address[1])
            state_zip = address[2].strip().split(" ")
        state = handle_missing(state_zip[0])
        zip_code = handle_missing(state_zip[1])
        phone = soup.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = re.sub(
            r"Closed.*",
            "",
            content[3].find("p").text.strip().replace("By Appointment Only", ""),
        ).replace(" – ", " - ")
        location_type = "OFFICE"
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
