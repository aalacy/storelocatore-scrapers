import csv
import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "lotaburger.com"
BASE_URL = "https://nationwidevision.com"
LOCATION_URL = "https://www.lotaburger.com/locations"
API_URL = "https://www.lotaburger.com/wp-admin/admin-ajax.php"

HEADERS = {
    "Accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "content-length": "43",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
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


def pull_content(url, method, data=[]):
    log.info("Pull content => " + url)
    if method == "POST":
        soup = bs(session.post(url, headers=HEADERS, data=data).content, "lxml")
    else:
        HEADERS_ = {
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }
        soup = bs(session.get(url, headers=HEADERS_).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    log.info("Fetching store_locator data")
    locations = []
    data = {"action": "find_locations", "address": "", "radius_val": "0"}
    soup = pull_content(API_URL, "POST", data)
    contents = soup.find_all("div", {"class": "voslrow locationlist"})
    get_store_info = pull_content(LOCATION_URL, "GET")
    store_info = get_store_info.body.find(
        "div", {"class": "content secPageContent"}
    ).find("div", {"id": "accordion-container"})
    for content in contents:
        full_address = (
            content.find("div", {"class": "callout"})
            .find("div", {"class": "col-lg-7"})
            .find("p")
            .get_text(strip=True, separator=",")
        )
        street_address = content.find("h4").get_text(strip=True).replace("X", "")
        details = (
            content.find("div", {"class": "locationdetails"})
            .find("div", {"class": "mainrow"})
            .find_all("div", {"class": "voslrow"})
        )
        latitude = content.find("div", {"class": "lat"}).text
        longitude = content.find("div", {"class": "long"}).text
        split_address = full_address.split(",")
        if len(split_address) == 3:
            city = split_address[1].replace(" ", "")
            state_zip = split_address[2].split(" ")
            state = state_zip[1]
            zip_code = state_zip[2]
        elif len(split_address) > 3:
            city = split_address[2].replace(" ", "")
            state_zip = split_address[3].split(" ")
            state = state_zip[1]
            zip_code = state_zip[2]

        if len(details) < 4:
            phone = details[1].get_text(strip=True)
            hours_of_operation = details[2].get_text(strip=True)
        else:
            phone = details[2].get_text(strip=True)
            hours_of_operation = details[3].get_text(strip=True)

        split_addr = street_address.split(",")
        filter = store_info.find(
            "a",
            text=re.compile(".*({}).*".format(" ".join(split_addr[0].split(" ")[:2]))),
        )
        if filter:
            master = filter.parent.parent.parent
            location_name = master.find(
                "div", {"class": "locationStoreName"}
            ).text.strip()
            store_number = re.findall(r"\d+", location_name)[0]
            info_content = master.find_all("div", {"class": "locationItemDesc"})
            phone = handle_missing(
                info_content[1].find("a").text.strip().replace("\t", ",")
            )
        else:
            filter = store_info.find(
                "a",
                text=re.compile(".*({}).*".format(zip_code)),
            )
            if filter:
                master = filter.parent.parent.parent
                location_name = master.find(
                    "div", {"class": "locationStoreName"}
                ).text.strip()
                store_number = re.findall(r"\d+", location_name)[0]
                info_content = master.find_all("div", {"class": "locationItemDesc"})
                phone = handle_missing(
                    info_content[1].find("a").text.strip().replace("\t", ",")
                )
            else:
                location_name = "<MISSING>"
                store_number = "<MISSING>"

        if hours_of_operation == "Temporarily CLOSED":
            hours_of_operation = "<MISSING>"

        country_code = "US"
        location_type = "<MISSING>"

        log.info("Append info to locations => " + street_address)
        locations.append(
            [
                DOMAIN,
                LOCATION_URL,
                location_name,
                street_address,
                handle_missing(city),
                handle_missing(state),
                handle_missing(zip_code),
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
    log.info("Finish processed {} locations".format(str(len(data))))


scrape()
