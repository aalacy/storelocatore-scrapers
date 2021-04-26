import csv
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "smittys.ca"
BASE_URL = "https://www.smittys.ca/Select-Location"
LOCATION_URL = "https://www.smittys.ca/Select-Location"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
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
    return field.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    stores = soup.find("div", {"id": "smittis-list"}).find_all(
        "div", {"class": "smitty-items"}
    )
    locations = []
    for row in stores:
        if int(row["rel"]) == 173:
            continue
        info = row.find("div", {"class": "result-details"})
        data = info.find("p").contents
        locator_domain = DOMAIN
        location_name = handle_missing(info.find("h2").text.strip())
        address = data[0].replace("Canada", "").strip().split(",")
        if len(address) >= 4:
            if len(address) > 4:
                street_address = ", ".join(address[:2])
                city = handle_missing(address[2])
                state = handle_missing(address[3])
            else:
                street_address = address[0]
                city = handle_missing(address[1])
                state = handle_missing(address[2])
            zip_code = handle_missing(address[-1])
        elif len(address) == 3:
            street_address = address[0]
            city = handle_missing(address[1])
            state_zip = address[2].strip().split(" ")
            state = handle_missing(state_zip[0])
            zip_code = handle_missing(address[2].replace(state, "").strip())
        else:
            if "10 Aquitania Boulevard" in address:
                street_address = ", ".join(address[:2])
                city = location_name.replace(" - West", "").strip()
            else:
                street_address = handle_missing(address[0])
                city = handle_missing(address[1])
            state = "<MISSING>"
            zip_code = "<MISSING>"
        country_code = "CA"
        store_number = row["rel"]
        phone = handle_missing(data[8].strip())
        location_type = "<MISSING>"
        hours = info.find("div", {"class": "restaurant_hours"})
        if hours:
            hours_of_operation = handle_missing(
                hours.get_text(strip=True, separator=",")
            )
        else:
            hours_of_operation = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
