import csv
from sgrequests import SgRequests
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("woolworths_com_au")


MAX_RESULTS = 1000


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


URL_TEMPLATE = (
    "https://www.woolworths.com.au/apis/ui/StoreLocator/Stores?Max="
    + str(MAX_RESULTS)
    + "&Division=SUPERMARKETS,PETROL,CALTEXWOW,METROCALTEX&Facility=&postcode={}"
)

search = (
    sgzip.ClosestNSearch()
)  # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize(country_codes=["au"])

session = SgRequests()

HEADERS = {
    "Accept": "*/*",
    "Method": "GET",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(hours):
    return ", ".join([x["TradingHourForDisplay"] for x in hours])


def fetch_data():
    keys = set()
    locations = []
    postcode = search.next_zip()
    while postcode:
        result_coords = []
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        url = URL_TEMPLATE.format(postcode)
        response = session.get(url, headers=HEADERS).json()
        stores = response["Stores"]
        for store in stores:
            latitude = handle_missing(store["Latitude"])
            longitude = handle_missing(store["Longitude"])
            result_coords.append((latitude, longitude))
            store_number = handle_missing(store["StoreNo"])
            key = store_number
            if key in keys:
                continue
            else:
                keys.add(key)
            locator_domain = "woolworths.com.au"
            page_url = "<MISSING>"
            location_name = handle_missing(store["Name"])
            street_address = handle_missing(store["AddressLine1"])
            city = handle_missing(store["Suburb"])
            state = handle_missing(store["State"])
            zip_code = handle_missing(store["Postcode"])
            country_code = "AU"
            phone = handle_missing(store["Phone"])
            location_type = handle_missing(store["Division"])
            hours_of_operation = parse_hours(store["TradingHours"])
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
        if len(stores) > 0:
            logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            logger.info("{} zero results!".format(postcode))
        postcode = search.next_zip()
    return locations


def scrape():
    data = fetch_data()
    write_output(data)


logger.info("scrape")
scrape()
