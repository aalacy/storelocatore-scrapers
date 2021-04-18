import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "dreamhotels.com"
BASE_URL = "https://www.dreamhotels.com/"
LOCATION_URL = "https://www.dreamhotels.com/default-en.html"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


accept_country = [
    {"US": ["United States"]},
    {
        "UK": [
            "United Kingdom",
            "Wales",
            "Greece",
            "England",
            "Northen Ireland",
            "Scotland",
        ]
    },
    {"CA": ["Canada"]},
]


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
    content = soup.find("div", {"class": "secondlevel"}).find(
        "ul", {"class": "destproperties"}
    )
    links = content.find("li", {"class": "firstpropertie withprop country"}).find_all(
        "a", {"href": True}
    )
    for link in links:
        if len(link["href"]) > 2:
            store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        soup = pull_content(page_url)
        content = soup.find("div", {"class": "grid grid--start"})
        address = (
            soup.select(".footer-directions-text")[0]
            .get_text()
            .strip()
            .replace("\n", ",")
            .split(",")
        )
        locator_domain = DOMAIN
        location_name = address[0]
        if len(address) == 3:
            street_address = " ".join(address[-2].split(" ")[:-2])
            city = address[-2].split(" ")[-3]
            state = address[-2].split(" ")[-2].upper()
            zip_code = address[-2].split(" ")[-1]
            phone = address[-1].split(":")[1].strip()
        elif len(address) == 5:
            street_address = " ".join(address[:-2])
            city = address[-3].strip()
            state = address[-2].split(" ")[-2].upper()
            zip_code = address[-2].split(" ")[-1]
            if "or" in address[-1].split(":")[1].strip():
                phone = address[-1].split(":")[1].strip().split("or")[0].strip()
            else:
                address[-1].split(":")[1].strip()
        street_address = (
            street_address.replace(city, "").replace(location_name, "").strip()
        )
        country_code = "USA"
        store_number = "<MISSING>"
        location_type = "Dream Hotels"
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
