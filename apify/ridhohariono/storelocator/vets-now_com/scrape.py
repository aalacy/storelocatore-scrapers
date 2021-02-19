import csv
import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "vets-now.com"
BASE_URL = "https://www.vets-now.com"
LOCATION_URL = "https://www.vets-now.com/clinics-sitemap.xml"
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


def parse_json(soup):
    info = soup.find("script", type="application/ld+json").string
    data = json.loads(info)
    return data


def fetch_store_urls():
    log.info("Fetching store URL")
    soup = pull_content(LOCATION_URL)
    store_urls = [
        val.text
        for val in soup.find_all(
            "loc", text=re.compile(r"\/find-an-emergency-vet\/\D+")
        )
    ]
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_urls = fetch_store_urls()
    locations = []
    for page_url in store_urls:
        soup = pull_content(page_url)
        info = parse_json(soup)["@graph"][5]
        locator_domain = DOMAIN
        location_name = handle_missing(info["name"])
        address = info["address"].replace(",,", ",")
        address = re.sub(r"<br.*", "", address)
        address = re.sub(r",$", "", address.strip()).split(",")
        del address[0]
        if len(address) > 2:
            if len(address) > 4:
                street_address = ", ".join(address[:-3]).strip()
                city = address[-3].strip()
            else:
                street_address = ", ".join(address[:-2]).strip()
                city = address[-2].strip()
            if "United Kingdom" in city:
                city = location_name.replace("Vets Now ", "").strip()
        else:
            street_address = address[0].strip()
            city = re.sub(
                r"[A-Z]{1,2}[0-9R][0-9A-Z]? [0-9][A-Z]{2}", "", address[1]
            ).strip()
        state = "<MISSING>"
        zip_code = handle_missing(
            re.findall(
                r"[A-Z]{1,2}[0-9A-Z]{1,2}[0-9A-Z]? [0-9][A-Z]{2}",
                ",".join(address).strip(),
            )[0]
        )
        country_code = "GB"
        store_number = "<MISSING>"
        phone = handle_missing(info["telephone"])
        hours_of_operation = (
            soup.find("ul", {"id": "clinic__opens"})
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
            .replace(",–,", " - ")
            .strip()
        )
        location_type = "<MISSING>"
        latitude = handle_missing(info["geo"]["latitude"])
        longitude = handle_missing(info["geo"]["longitude"])
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
