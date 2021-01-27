import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "ernestjones.co.uk"
BASE_URL = "https://www.ernestjones.co.uk"
LOCATION_URL = "https://www.ernestjones.co.uk/webstore/secure/viewAllStores.sdo"
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


def find_meta(soup, tag, query):
    data = soup.find(tag, query)
    return handle_missing(data["content"])


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("section", {"class": "search-results"}).find(
        "div", {"class": "search-results__body"}
    )
    stores = content.find_all("div", {"class": "search-results__store"})
    for store in stores:
        link = store.find("a", {"class": "store--location__link"})
        address_phone = store.find("section", {"class": "store-address"}).get_text(
            strip=True, separator=","
        )
        hoo = store.find("div", {"class": "store-opening-time"}).get_text(
            strip=True, separator=" "
        )
        store_dict = {
            "title": link.text.strip(),
            "link": BASE_URL + link["href"],
            "store_number": link["data-store-number"],
            "address_phone": address_phone,
            "hoo": hoo,
        }
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
        locator_domain = DOMAIN
        location_name = handle_missing(row["title"])
        street_address = find_meta(
            soup, "meta", {"property": "business:contact_data:street_address"}
        )
        city = find_meta(soup, "meta", {"property": "business:contact_data:locality"})
        state = "<MISSING>"
        zip_code = find_meta(
            soup, "meta", {"property": "business:contact_data:postal_code"}
        )
        country_code = "UK"
        store_number = row["store_number"]
        phone = find_meta(
            soup, "meta", {"property": "business:contact_data:phone_number"}
        )
        check_status = soup.find("div", {"class": "SG081-storeClosed-message"})
        if check_status and "Temporarily Closed" in check_status.text.strip():
            location_type = "TEMP_CLOSED"
        else:
            location_type = "OPEN"
        hours_of_operation = handle_missing(row["hoo"])
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
