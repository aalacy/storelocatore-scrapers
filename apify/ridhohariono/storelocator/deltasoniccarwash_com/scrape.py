import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "deltasoniccarwash.com"
BASE_URL = "https://deltasoniccarwash.com/"
LOCATION_URL = "https://deltasoniccarwash.com/locations.html"
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
    contents = soup.find_all("div", {"class": "location-links1"})
    for content in contents:
        urls = content.find_all("a", {"data-href": re.compile(r"page:.*")})
        for url in urls:
            if len(url.text) > 0:
                store_dict = {"link": BASE_URL + url["href"], "address": url.text}
                store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    sotre_info = fetch_store_urls()
    locations = []
    for row in sotre_info:
        page_url = row["link"]
        soup = pull_content(page_url)
        content = soup.find(
            "div", {"class": "location-links1", "data-muse-type": "txt_frame"}
        )
        locator_domain = DOMAIN
        parent = content.find("h1", {"class": "Location-H1-Heading"})
        location_name = parent.text
        addr_detail = (
            content.find(text=re.compile(r"\D+,\D{2,3}\s+\d+"))
            .parent.get_text(strip=True, separator=",")
            .split(",")
        )
        street_address = addr_detail[0]
        city = addr_detail[1]
        state = re.sub(r"\d+", "", addr_detail[2]).strip()
        zip_code = re.sub(r"\D+", "", addr_detail[2]).strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            content.find("a", {"href": re.compile(r"tel:.*")})["href"]
            .replace("tel:", "")
            .strip()
        )
        get_hoo = content.find("h3", text="Car Wash")
        hours_of_operation = get_hoo.find_next("p").get_text(strip=True, separator=",")
        if "Coming soon" in hours_of_operation:
            location_type = "COMING_SOON"
        else:
            location_type = "OPEN"
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
