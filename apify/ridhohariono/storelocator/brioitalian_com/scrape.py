import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "https://brioitalian.com/"
BASE_URL = "https://locations.brioitalian.com/"
LOCATION_URL = "https://locations.brioitalian.com/us"
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
    content = soup.find("ul", {"class": "c-directory-list-content"})
    state_links = content.find_all("li", {"class": "c-directory-list-content-item"})
    for row in state_links:
        count = row.find("span").text.replace(")", "").replace("(", "")
        if int(count) > 1:
            data = pull_content(BASE_URL + row.find("a")["href"])
            content = data.find("ul", {"class": "c-directory-list-content"})
            li_parent = data.find_all("li", {"class": "c-directory-list-content-item"})
            for li in li_parent:
                count_child = li.find("span").text.replace(")", "").replace("(", "")
                if int(count_child) > 1:
                    data = pull_content(BASE_URL + li.find("a")["href"])
                    content = data.find(
                        "div", {"class": "container location-list-container"}
                    )
                    links_child = data.find_all(
                        "a", {"class": "Link Link--primary Link--lower"}
                    )
                    for link_child in links_child:
                        store_urls.append(
                            BASE_URL + link_child["href"].replace("../../", "")
                        )
                else:
                    link = li.find("a", {"class": "c-directory-list-content-item-link"})
                    store_urls.append(BASE_URL + link["href"].replace("..", ""))
        else:
            link = row.find("a", {"class": "c-directory-list-content-item-link"})
            store_urls.append(BASE_URL + link["href"].replace("..", ""))
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
            soup.find("meta", {"property": "og:title"})["content"]
        )
        address = soup.find("address", {"id": "address"})
        street_address = address.find("span", {"class": "c-address-street"}).get_text(
            strip=True, separator=","
        )
        city = handle_missing(
            address.find("span", {"itemprop": "addressLocality"}).text.strip()
        )
        state = handle_missing(address.find("span", {"class": "c-address-state"}).text)
        zip_code = handle_missing(
            address.find("span", {"class": "c-address-postal-code"}).text.strip()
        )
        country_code = "US"
        store_number = "<MISSING>"
        phone = soup.find("span", {"id": "telephone"}).text.strip()
        hours_of_operation = parse_hours(
            soup.find("table", {"class": "c-location-hours-details"})
        )
        location_type = "<MISSING>"
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
