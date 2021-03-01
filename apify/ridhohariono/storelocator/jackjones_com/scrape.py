import csv
from sgrequests import SgRequests
from sglogging import sglog

DOMAIN = "jackjones.com"
BASE_URL = "https://www.jackjones.com"
COUNTRY_LIST = ["CA", "GB"]
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
    return field


def get_state_url():
    URL = "https://www.jackjones.com/on/demandware.store/Sites-BSE-NL-Site/en_NL/Stores-GetCities?countryCode={country_code}&brandCode=jj"
    URL_STATE = "https://www.jackjones.com/on/demandware.store/Sites-BSE-NL-Site/en_NL/PickupLocation-GetLocations?countryCode={country}&brandCode=jj&postalCodeCity={state}&serviceID=SDSStores&filterByClickNCollect=false"
    result = []
    for row in COUNTRY_LIST:
        log.info("Get State information for => " + row)
        data = session.get(URL.format(country_code=row), headers=HEADERS).json()
        log.info("Found {} state on {}".format(len(data), row))
        for state in data:
            result.append(URL_STATE.format(country=row, state=state))
    log.info("Total state URL = {}".format(len(result)))
    return result


def fetch_data():
    state_url = get_state_url()
    locations = []
    for url in state_url:
        data = session.get(url, headers=HEADERS).json()
        if "locations" not in data:
            continue
        for row in data["locations"]:
            page_url = "https://www.jackjones.com/nl/en/stores"
            locator_domain = DOMAIN
            location_name = handle_missing(row["storeName"])
            if "address2" in row and len(row["address2"]) > 0:
                street_address = "{}, {}".format(row["address1"], row["address2"])
            else:
                street_address = row["address1"]
            city = handle_missing(row["city"])
            state = "<MISSING>" if "state" not in row else row["state"]
            zip_code = handle_missing(row["postalCode"])
            country_code = row["country"]
            store_number = row["storeID"]
            phone = handle_missing(row["phone"])
            location_type = "<MISSING>"
            latitude = handle_missing(row["latitude"])
            longitude = handle_missing(row["longitude"])
            hours_of_operation = "<MISSING>"
            log.info(
                "Append info to locations: {} : {}".format(
                    location_name, street_address
                )
            )
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
