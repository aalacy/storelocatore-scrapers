import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
import re


DOMAIN = "larosagrill.com"
BASE_URL = "https://larosagrill.com"
LOCATION_URL = "https://larosagrill.com/menu-locations"
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


def fetch_data():
    log.info("Fetching store_locator data")
    # page_urls = fetch_store_urls()
    soup = pull_content(LOCATION_URL)
    content = (
        soup.find_all("div", {"class": "blog"})[1]
        .find("div", {"class": "container"})
        .find_all("div", {"class": "marginall-5"})
    )
    locations = []
    for row in content:
        locator_domain = DOMAIN
        location_name = handle_missing(
            row.find("div", {"class": "locationheader"}).text.strip()
        )
        address = (
            row.find("div", {"style": "margin:5px 0;color:white;text-align:center;"})
            .get_text(strip=True, separator=",")
            .replace(",,", ",")
            .split(",")
        )
        coming_soon = row.find("img", {"src": "images/coming soon.jpg"})
        if not coming_soon:
            if len(address) > 1:
                street_address = address[0].strip()
                city = address[1].strip()
                state = re.sub(r"\d+", "", address[2]).strip()
                zip_code = re.sub(r"r\D+", "", address[2]).strip()
                if len(address) < 4:
                    city = "<MISSING>"
                    state = address[1]
                    zip_code = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = row.find("div", {"class": "locationheader1"})
            if not phone:
                phone = "<MISSING>"
            else:
                phone = phone.find("a", {"style": "border:0px;padding:0;"})[
                    "href"
                ].replace("tel:", "")

            hours_of_operation = "<MISSING>"
            hoo = row.find("a", text=re.compile(r"OPEN\s+HOURS"))
            if hoo:
                hours_of_operation = (
                    hoo.find_next("a").text.replace("Open Daily", "").strip()
                )
            location_type = "<MISSING>"
            latlong = row.find("a", {"href": re.compile(r"www.google.com/maps")})
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            if latlong:
                latlong = re.search(r"\@(\d+.*)", latlong["href"]).group(1).split(",")
                latitude = latlong[0]
                longitude = latlong[1]
            log.info("Append {} => {}".format(location_name, street_address))
            locations.append(
                [
                    locator_domain,
                    LOCATION_URL,
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
