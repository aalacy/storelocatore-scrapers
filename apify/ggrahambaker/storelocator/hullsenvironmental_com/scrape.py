import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sglogging import sglog

DOMAIN = "hullsenvironmental.com"
BASE_URL = "https://www.hullsenvironmental.com/"
LOCATION_URL = "https://www.hullsenvironmental.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field.replace(u"\u200b", "")


def fetch_data():
    soup = bs(session.get(LOCATION_URL, headers=HEADERS).content, "lxml")
    div = soup.find("div", {"class": "lm-left"})
    contents = div.find_all("p")
    locations = []
    for row in contents:
        info = row.get_text(strip=True, separator="|").split("|")
        location_name = handle_missing(row.find("strong").text.strip())
        street_address = handle_missing(info[1].strip())
        city_state_zip = info[2].split(",")
        city = handle_missing(city_state_zip[0].strip())
        state = handle_missing(re.sub(r"\d+", "", city_state_zip[1]).strip())
        zip_code = handle_missing(re.sub(r"\D+", "", city_state_zip[1]).strip())
        country_code = "US"
        store_number = "<MISSING>"
        phone = handle_missing(info[4].strip())
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        log.info("Append {} => {}".format(location_name, street_address))
        locations.append(
            [
                DOMAIN,
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
