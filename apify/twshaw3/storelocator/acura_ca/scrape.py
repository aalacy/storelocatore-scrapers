import csv
from sgrequests import SgRequests
import sgzip
import os
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("acura_ca")


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


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
}

URL_TEMPLATE = "https://api.honda.ca/dealer/A/Live/dealers/{}/{}/with-driving-distance?AcceptLanguage=en"

search = (
    sgzip.ClosestNSearch()
)  # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize(country_codes=["ca"])

session = SgRequests()


def handle_missing(field):
    if field == None or (type(field) == type("x") and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def fetch_data():
    keys = set()
    locations = []
    coord = search.next_coord()
    while coord:
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        url = URL_TEMPLATE.format(coord[0], coord[1])
        stores = session.get(url, headers=HEADERS).json()["Items"]
        logger.info(len(stores))
        result_coords = []
        for store in stores:
            data = store["Dealer"]
            store_number = handle_missing(str(data["Id"]))
            latitude = handle_missing(data["Location"]["Coordinate"]["Latitude"])
            longitude = handle_missing(data["Location"]["Coordinate"]["Longitude"])
            result_coords.append((latitude, longitude))
            street_address = handle_missing(data["Location"]["Address"])
            city = handle_missing(data["Location"]["City"]["Name"])
            state = handle_missing(data["Location"]["Province"]["Name"])
            zip_code = handle_missing(data["Location"]["PostalCode"]["Value"])
            key = "{}|{}|{}|{}".format(street_address, city, state, zip_code)
            if key not in keys:
                keys.add(key)
                locator_domain = "acura.ca"
                country_code = "CA"
                location_name = handle_missing(data["Name"])
                location_type = "<MISSING>"
                page_url = handle_missing(data["ContactInformation"]["Website"])
                phone = handle_missing(
                    data["ContactInformation"]["Phones"][0]["Number"]
                )
                hours_of_operation = str(
                    handle_missing(data["Departments"][0]["Hours"])
                )
                record = [
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
                locations.append(record)
        if len(stores) == 0:
            logger.info("max distance update")
            search.max_distance_update(100.0)
        else:
            logger.info("max count update")
            search.max_count_update(result_coords)
        coord = search.next_coord()
    return locations


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
