import csv
from sgrequests import SgRequests
from sglogging import sglog


DOMAIN = "stoptosavesupermarket.com"
BASE_URL = "https://stoptosavesupermarket.com"
LOCATION_URL = "https://stoptosavesupermarket.com/contact"
API_URL = "https://stoptosavesupermarket.com/ajax/index.php"
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


def fetch_data():
    log.info("Fetching store_locator data")
    data = {
        "method": "POST",
        "apiurl": "https://stoptosavesupermarket.rsaamerica.com/Services/SSWebRestApi.svc/GetClientStores/1",
    }
    store_lists = session.post(API_URL, headers=HEADERS, data=data).json()
    locations = []
    for row in store_lists["GetClientStores"]:
        page_url = LOCATION_URL
        locator_domain = DOMAIN
        location_name = handle_missing(row["ClientStoreName"])
        street_address = handle_missing(row["AddressLine1"])
        city = handle_missing(row["City"])
        state = handle_missing(row["StateName"])
        zip_code = handle_missing(row["ZipCode"])
        phone = handle_missing(row["StorePhoneNumber"])
        hours_of_operation = handle_missing(row["StoreTimings"])
        country_code = "US"
        store_number = row["StoreNumber"]
        location_type = "stoptosavesupermarket"
        latitude = handle_missing(row["Latitude"])
        longitude = handle_missing(row["Longitude"])
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
