import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import usaddress


DOMAIN = "grindfitness24hour.com"
BASE_URL = "http://www.grindfitness24hour.com/"
LOCATION_URL = "http://www.grindfitness24hour.com/locations.html"
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
    a_class = "OBJ-11 ActiveButton OBJ-12"
    alinks = soup.find_all("a", {"class": a_class})
    for link in alinks:
        store_urls.append(BASE_URL + link["href"])
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        locator_domain = DOMAIN
        info = soup.find("img", {"id": "art_8"})["alt"].split(" Location ")
        location_name = info[0]
        parse_addr = usaddress.tag(info[1])
        if "StateName" in parse_addr[0]:
            state = parse_addr[0]["StateName"]
        else:
            state = info[1].split()[-1]
        city = parse_addr[0]["PlaceName"].replace(state, "").strip()
        street_address = info[1].replace(city, "").replace(state, "").strip()
        zip_code = "<MISSING>"
        phone = (
            soup.find("span", text=re.compile(r"Questions.*"))
            .text.replace("Questions? Text Laura at ", "")
            .strip()
        )
        country_code = "US"
        store_number = "<MISSING>"
        hours_of_operation = "24 Hours"
        location_type = "grindfitness24hour"
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
