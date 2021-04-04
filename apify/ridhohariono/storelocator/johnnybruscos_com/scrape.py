import csv
import usaddress
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "johnnybruscos.com"
BASE_URL = "https://johnnybruscos.com/"
LOCATION_URL = "https://johnnybruscos.com/all-locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "Connection": "keep-alive",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()


def write_output(data):
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
    soup = bs(session.get(url, headers=HEADERS).content, "html.parser")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(hours):
    el = hours.split(",")
    if el:
        del el[0]
        return ", ".join([str(x) for x in el]).replace(":, ", ": ")


def get_state_url():
    soup = pull_content(LOCATION_URL)
    state_urls = [
        x["href"] for x in soup.find("ul", {"id": "menu-states"}).find_all("a")
    ]
    log.info("Found {} state urls!".format(len(state_urls)))
    return state_urls


def fetch_data():
    state_urls = get_state_url()
    locations = []
    for state_url in state_urls:
        log.info("Get store locator informations for " + state_url)
        soup = pull_content(state_url)
        for x in soup.find_all("div", {"class": "wpseo-result"}):
            link = x.find("a", {"class": "result-title"})
            if link:
                page_url = link["href"]
                store_content = pull_content(page_url)
                store_info = store_content.find(
                    "div", {"class": "site-inner single-site-inner"}
                ).find("div", {"class": "wrap"})
                locator_domain = DOMAIN
                location_name = store_info.find(
                    "h4", {"class": "single-name"}
                ).text.replace("–", "-")
                full_address = store_info.find(
                    "div", {"class": "store-address"}
                ).get_text(strip=True, separator=",")
                street_address = (
                    store_info.find("div", {"class": "store-address"})
                    .contents[0]
                    .strip()
                ).replace(".", "")
                parse_addr = usaddress.tag(full_address)
                city = handle_missing(parse_addr[0]["PlaceName"])
                state = handle_missing(parse_addr[0]["StateName"])
                zip_code = handle_missing(parse_addr[0]["ZipCode"])
                country_code = "US"
                store_number = "<MISSING>"
                phone = store_content.find("div", {"class": "store-phone"}).get_text(
                    strip=True
                )
                location_type = "<MISSING>"
                latitude = handle_missing(
                    store_content.find("meta", property="place:location:latitude")[
                        "content"
                    ]
                )
                longitude = handle_missing(
                    store_content.find("meta", property="place:location:longitude")[
                        "content"
                    ]
                )
                hours_content = store_content.find("div", {"class": "hours"})
                hours = hours_content.get_text(strip=True, separator=",")
                hours_of_operation = handle_missing(parse_hours(hours))
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
