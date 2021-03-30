import csv
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "elevationburger.com"
BASE_URL = "https://locations.elevationburger.com/"
LOCATION_URL = "https://locations.elevationburger.com/locations.json"
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(hour_content):
    hoo = []
    for row in hour_content:
        start = str(row["intervals"][0]["start"])
        end = str(row["intervals"][0]["end"])
        hours = "{}:{} - {}:{}".format(start[:2], start[-2:], end[:2], end[-2:])
        hoo.append(row["day"] + ": " + hours)
    return ", ".join(hoo)


def fetch_data():
    store_info = session.get(LOCATION_URL, headers=HEADERS).json()
    locations = []
    for row in store_info["locations"]:
        info = row["loc"]
        country_code = info["country"]
        if country_code == "US":
            page_url = BASE_URL + row["url"]
            location_name = handle_missing(
                info["name"] + " " + info["customByName"]["Geomodifier"].strip()
            )
            if "address2" in info and len(info["address2"]) > 0:
                street_address = "{}, {}".format(info["address1"], info["address2"])
            else:
                street_address = info["address1"]
            city = handle_missing(info["city"])
            state = handle_missing(info["state"])
            zip_code = handle_missing(info["postalCode"])
            store_number = info["id"]
            phone = handle_missing(info["phone"])
            latitude = handle_missing(info["latitude"])
            longitude = handle_missing(info["longitude"])
            hours_of_operation = parse_hours(info["hours"]["days"])
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
