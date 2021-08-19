import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import sglog

DOMAIN = "pizzagogo.co.uk"
BASE_URL = "https://www.pizzagogo.co.uk/"
LOCATION_URL = "https://www.pizzagogo.co.uk/ajax/?do=all_stores_for_map"
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


def get_hours(page_url):
    soup = pull_content(page_url)
    content = soup.find("table", {"class": "padded_table"})
    hoo = content.get_text(strip=True, separator=",")
    return hoo.replace(":,", ": ")


def split_info(val):
    return val.split("|")


def fetch_data():
    store_json = session.get(LOCATION_URL, headers=HEADERS).json()
    store_info = {
        "store_ids": split_info(store_json["store_ids"]),
        "stores": split_info(store_json["stores"]),
        "address": split_info(store_json["address_arr"]),
        "phone": split_info(store_json["phone_arr"]),
        "lat": split_info(store_json["lat_arr"]),
        "lng": split_info(store_json["lng_arr"]),
    }
    locations = []
    for i in range(len(store_info["store_ids"])):
        store_number = store_info["store_ids"][i]
        page_url = BASE_URL + "gotostore/{}".format(store_number)
        location_name = handle_missing(store_info["stores"][i])
        parse_addr = (
            store_info["address"][i]
            .replace("\r", ",")
            .replace("<br />", ",")
            .strip()
            .replace(",,", ",")
        )
        address = re.sub(r",\s+,", ",", parse_addr).strip().split(",")
        if len(address) > 4:
            street_address = ", ".join(address[:2])
        else:
            street_address = address[0].strip()
        if len(address) > 2:
            if len(address) > 4:
                city = address[2].strip()
            else:
                city = address[1].strip()
        else:
            city = "<MISSING>"
        state = "<MISSING>"
        zip_code = address[-1].strip()
        phone = store_info["phone"][i]
        country_code = "GB"
        latitude = store_info["lat"][i]
        longitude = store_info["lng"][i]
        hours_of_operation = get_hours(page_url)
        location_type = "<MISSING>"
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
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
