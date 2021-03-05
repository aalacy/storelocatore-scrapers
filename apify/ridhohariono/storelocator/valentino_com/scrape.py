import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "valentino.com"
BASE_URL = "https://boutiques.valentino.com/"
LOCATION_URL = "https://boutiques.valentino.com/directory"
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


def parse_hours(table):
    data = table.find("tbody")
    days = data.find_all("td", {"class": "c-hours-details-row-day"})
    hours = data.find_all("td", {"class": "c-hours-details-row-intervals"})
    hoo = []
    for i in range(len(days)):
        hours_formated = "{}: {}".format(days[i].text, hours[i].text)
        hoo.append(hours_formated)
    return ", ".join(hoo)


def fetch_store_urls():
    log.info("Fetching store URL")
    store_urls = []
    soup = pull_content(LOCATION_URL)
    content = soup.find("div", {"class": "Directory-content"})
    country_links = [
        content.find("a", text="United States"),
        content.find("a", text="United Kingdom"),
        content.find("a", text="Canada"),
    ]
    for c_link in country_links:
        count = c_link["data-count"].replace("(", "").replace(")", "")
        if int(count) > 1:
            soup = pull_content(BASE_URL + c_link["href"])
            info = soup.find("div", {"class": "Directory-content"})
            store_links = info.find_all("a", {"class": "Teaser-titleLink"})
            for row in store_links:
                store_urls.append(BASE_URL + row["href"].replace("../", ""))
        else:
            store_urls.append(BASE_URL + c_link["href"].replace("../", ""))
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        location_name = handle_missing(
            soup.find("span", {"id": "location-name"}).get_text(
                strip=True, separator=" | "
            )
        )
        address = soup.find("address", {"id": "address"})
        street_address = address.find("meta", {"itemprop": "streetAddress"})["content"]
        city = handle_missing(
            address.find("meta", {"itemprop": "addressLocality"})["content"]
        )
        check_state = address.find("abbr", {"itemprop": "addressRegion"})
        if not check_state:
            state = "<MISSING>"
        else:
            state = handle_missing(check_state.text)
        zip_code = handle_missing(
            address.find("span", {"class": "c-address-postal-code"}).text.strip()
        )
        country_code = address["data-country"]
        store_number = "<MISSING>"
        phone = soup.find("div", {"id": "phone-main"}).text.strip()
        hours_of_operation = parse_hours(
            soup.find("table", {"class": "c-hours-details"})
        )
        hours = soup.find_all("td", {"class": "c-hours-details-row-intervals"})
        if all(value.text == "Closed" for value in hours):
            location_type = "TEMP_CLOSED"
        else:
            location_type = "OPEN"
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
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
