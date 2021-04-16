import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "aman.com"
BASE_URL = "https://www.aman.com"
LOCATION_URL = "https://www.aman.com/"
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
    content = soup.find("section", {"class": "quicklinks-bar"}).find(
        "div", {"class": "destination-quick-links"}
    )
    links = content.find_all("a", {"class": "clean"})
    print(len(links))
    for link in links:
        store_urls.append(BASE_URL + link["href"])
    print(store_urls)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    page_urls = fetch_store_urls()
    locations = []
    for page_url in page_urls:
        soup = pull_content(page_url)
        content = soup.find("div", {"class": "grid grid--start"})
        address = content.find("address").get_text(strip=True, separator=",").split(",")

        locator_domain = DOMAIN
        country = address[-1]
        for row in accept_country:
            for key, value in row.items():
                if country in value:
                    # print("{} => {}".format(country, key))
                    location_name = handle_missing(
                        content.find("h3", {"class": "heading-h"}).text.strip()
                    )
                    city = "<MISSING>"
                    if len(address) > 3:
                        if country == "Greece":
                            street_address = address[0]
                            city = address[1]
                        else:
                            street_address = ", ".join(address[:2])
                            state = re.sub(
                                r"\d+", "", address[2].replace("-", "")
                            ).strip()
                        zip_code = re.sub(r"\D+", "", address[2].split("-")[0]).strip()
                    else:
                        street_address = address[0]
                        state = re.sub(r"\d+", "", address[1].replace("-", "")).strip()
                        zip_code = re.sub(r"\D+", "", address[1].split("-")[0]).strip()
                    country_code = key
                    store_number = "<MISSING>"
                    phone = handle_missing(
                        content.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
                    )
                    location_type = "<MISSING>"
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
