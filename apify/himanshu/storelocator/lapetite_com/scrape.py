import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re


DOMAIN = "lapetite.com"
BASE_URL = "https://www.lapetite.com"
LOCATION_URL = "https://www.lapetite.com/child-care-centers/find-a-school/"
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
    soup = bs(session.get(url, headers=HEADERS).content, "html.parser")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(table):
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-location-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-location-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    state_links = soup.find("map", {"name": "USMap"}).find_all("area")
    for row in state_links:
        data = pull_content(BASE_URL + row["href"])
        content = data.find("section", {"class": "page-content fys_results"}).find_all(
            "div", {"class": "locationCard", "data-school-id": True}
        )
        for row in content:
            links = row.find_all("a", {"class": "schoolNameLink"})
            for link in links:
                if "https" in link["href"]:
                    store_urls.append(link["href"])
                else:
                    store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        if page_url == "https://www.childtime.com/1511":
            continue
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        location_name = handle_missing(
            soup.find("div", {"class": "local-school-header hero"})
            .find("h1")
            .text.strip()
        )
        address = soup.find("span", {"class": "addr"})
        street_address = address.find("span", {"class": "street"}).text.strip()
        cityState = address.find("span", {"class": "cityState"}).text.strip().split(",")
        city = cityState[0].strip()
        state = re.sub(r"\d+", "", cityState[1].strip()).strip()
        zip_code = re.sub(r"\D+", "", cityState[1].strip()).strip()
        country_code = "US"
        store_number = soup.find(
            "div", {"class": "school-info", "data-school-id": True}
        )["data-school-id"]
        phone = soup.find("span", {"class": "tel show-for-large"}).text.strip()
        hours_of_operation = (
            soup.find("svg", {"class": "openHours"})
            .parent.text.strip()
            .replace("Open:", "")
            .strip()
        )
        location_type = "La Petite Academy"
        latitude = address["data-latitude"]
        longitude = address["data-longitude"]
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
