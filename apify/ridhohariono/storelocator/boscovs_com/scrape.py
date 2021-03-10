import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "boscovs.com"
BASE_URL = "https://locations.boscovs.com/"
LOCATION_URL = "https://locations.boscovs.com/index.html"
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


def parse_hours(element):
    if element:
        hours = element.find("tbody").find_all("tr")
        hoo = ""
        i = 1
        for row in hours:
            hoo += row["content"] if i == 1 else ", " + row["content"]
            i += 1
    else:
        hoo = "<MISSING>"
    return hoo


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("ul", {"class": "Directory-list"})
    state_urls = content.find_all("a", {"class": "Directory-listLink"})
    for state_url in state_urls:
        links_count = state_url["data-count"].replace("(", "").replace(")", "")
        if int(links_count) > 1:
            store_info = pull_content(BASE_URL + state_url["href"])
            store_links = store_info.find_all("a", {"data-ya-track": "visitpage"})
            for link in store_links:
                store_urls.append(BASE_URL + link["href"])
        else:
            store_urls.append(BASE_URL + state_url["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    sotre_info = fetch_store_urls()
    locations = []
    for page_url in sotre_info:
        soup = pull_content(page_url)
        content = soup.find("div", {"class": "Core-col Core-col--fixedWidth"})
        locator_domain = DOMAIN
        location_name = content.find("span", {"class": "LocationName"}).text.strip(" ")
        address = content.find("address", {"id": "address"})
        street_address = address.find("meta", {"itemprop": "streetAddress"})["content"]
        city = address.find("span", {"class": "c-address-city"}).text
        state = address.find("abbr", {"class": "c-address-state"}).text
        zip_code = handle_missing(
            address.find("span", {"class": "c-address-postal-code"}).text
        )
        country_code = address["data-country"]
        store_number = "<MISSING>"
        phone = handle_missing(content.find("div", {"id": "phone-main"}).text)
        hours_of_operation = parse_hours(
            content.find("table", {"class": "c-hours-details"})
        )
        location_type = "<MISSING>"
        latitude = handle_missing(
            content.find("meta", {"itemprop": "latitude"})["content"]
        )
        longitude = handle_missing(
            content.find("meta", {"itemprop": "longitude"})["content"]
        )
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
