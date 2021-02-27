import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "outfitfashion.com"
BASE_URL = "https://stores.outfitfashion.com/"
LOCATION_URL = "https://stores.outfitfashion.com/index.html"
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
    content = soup.find("ul", {"class": "Directory-listLinks"})
    links = content.find_all("a", {"class": "Directory-listLink"})
    print(links)
    for link in links:
        count = link["data-count"].replace(")", "").replace("(", "")
        if int(count) > 1:
            data = pull_content(BASE_URL + link["href"])
            content = data.find("ul", {"class": "Directory-listTeasers Directory-row"})
            link = data.find_all("a", {"data-ya-track": "visitpage"})
            for row in link:
                store_urls.append(BASE_URL + row["href"])
        else:
            store_urls.append(BASE_URL + link["href"])
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
            soup.find("span", {"class": "LocationName"}).get_text(
                strip=True, separator=" | "
            )
        )
        addr1 = soup.find("span", {"class": "c-address-street-1"})
        addr2 = soup.find("span", {"class": "c-address-street-2"})
        if addr2:
            street_address = "{}, {}".format(addr1.text, addr2.text)
        else:
            street_address = addr1.text
        city = handle_missing(soup.find("span", {"class": "c-address-city"}).text)
        state = handle_missing(
            soup.find("meta", {"itemprop": "addressLocality"})["content"]
        )
        zip_code = handle_missing(
            soup.find("span", {"class": "c-address-postal-code"}).text
        )
        country_code = handle_missing(
            soup.find("address", {"id": "address"})["data-country"]
        )
        store_number = "<MISSING>"
        phone = soup.find("div", {"id": "phone-main"}).text
        hours = soup.find_all("td", {"class": "c-hours-details-row-intervals"})
        if all(value.text == "Closed" for value in hours):
            location_type = "CLOSED"
        else:
            location_type = "OPEN"
        hours_of_operation = parse_hours(
            soup.find("table", {"class": "c-hours-details"})
        )
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
