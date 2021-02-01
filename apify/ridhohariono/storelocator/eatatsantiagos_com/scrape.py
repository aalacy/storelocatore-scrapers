import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "eatatsantiagos.com"
BASE_URL = "https://eatatsantiagos.com"
LOCATION_URL = (
    "https://eatatsantiagos.com/santiagos-mexican-restaurant-locations-colorado"
)
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
    content = soup.find("section", {"id": "oms_74527532750"})
    store_info = content.find_all(
        "div", {"class": "col-12 col-sm-6 col-md-4 col-xl-3 my-3 count"}
    )
    for row in store_info:
        info = row.find("div", {"class": "bg-white border shadow p-3 h-100"})
        title = info.find("h5").text
        link = row.find("a", {"class": "btn btn-sm btn-primary"})
        address = info.find("p").text
        store_dict = {
            "title": title,
            "link": BASE_URL + link["href"],
            "address": address,
        }
        store_urls.append(store_dict)
    log.info("Found {} URL ".format(len(store_urls)))
    return store_urls


def fetch_data():
    log.info("Fetching store_locator data")
    store_info = fetch_store_urls()
    locations = []
    for row in store_info:
        page_url = row["link"]
        soup = pull_content(page_url)
        content = soup.find("div", {"class": "container-fluid whitebanner2 snip"})
        locator_domain = DOMAIN
        location_name = handle_missing(content.find("h3", {"class": "title"}).text)
        address = row["address"].split(",")
        if len(address) == 4:
            street_address = ", ".join(address[:2]).strip()
            city = handle_missing(address[2].strip())
            state = re.sub(r"\d+", "", address[3]).strip()
            zip_code = re.sub(r"\D", "", address[3]).strip()
        elif len(address) < 4:
            street_address = address[0].strip()
            city = handle_missing(address[1].strip())
            state = re.sub(r"\d+", "", address[2]).strip()
            zip_code = re.sub(r"\D", "", address[2]).strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = content.find("div", {"class": "phone"}).text.strip()
        location_type = "<MISSING>"
        hours_of_operation = (
            content.find("div", {"class": "hours"}).text.replace("Hours:", "").strip()
        )
        if len(hours_of_operation.split(",")) > 2:
            hoo = content.find_all("div", {"class": "hours"})
            hours_of_operation = "".join(
                [hoo[x].text.replace("Hours:", "").strip() for x in range(0, 2)]
            )
        elif (
            "Sundays" not in hours_of_operation
            and len(hours_of_operation.split(",")) == 2
        ):
            hours_of_operation = (
                hours_of_operation + content.find_all("div", {"class": "hours"})[1].text
            )
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
