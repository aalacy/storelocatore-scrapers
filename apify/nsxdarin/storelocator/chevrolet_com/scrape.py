import csv
from datetime import datetime
from sgzip import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger("chevrolet_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "locale": "en_US",
}

fields = [
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


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(fields)
        for row in data:
            writer.writerow(row)


MISSING = "<MISSING>"


def get(data, key):
    return data.get(key, MISSING) or MISSING


days = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}


def get_hours(location):
    hours = (
        location.get("generalOpeningHour")
        or location.get("serviceOpeningHour")
        or location.get("partsOpeningHour")
    )
    if not hours:
        return MISSING

    hours_of_operation = []

    for hour in hours:
        for day in hour.get("dayOfWeek"):
            hours_of_operation.append(
                f"{days[day]} {hour.get('openFrom')}-{hour.get('openTo')}"
            )

    return ",".join(hours_of_operation)


def extract(location):
    locator_domain = "chevrolet.com"
    page_url = get(location, "dealerUrl")
    store_number = get(location, "id")
    location_name = get(location, "dealerName")

    contact = location.get("generalContact")
    phone = get(contact, "phone1")

    address = location.get("address")
    street_address = get(address, "addressLine1")
    city = get(address, "cityName")
    state = get(address, "countrySubdivisionCode")
    postal = get(address, "postalCode")
    country_code = get(address, "countryIso")

    geolocation = location.get("geolocation")
    latitude = get(geolocation, "latitude")
    longitude = get(geolocation, "longitude")

    hours_of_operation = get_hours(location)
    location_type = MISSING

    return {
        "locator_domain": locator_domain,
        "page_url": page_url,
        "store_number": store_number,
        "location_name": location_name,
        "location_type": location_type,
        "phone": phone,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip": postal,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "hours_of_operation": hours_of_operation,
    }


MAX_DISTANCE = 50
MAX_RESULTS = 50


def fetch_location(coord, retry_count=0):
    try:
        lat, lng = coord
        params = {"distance": MAX_DISTANCE, "maxResults": MAX_RESULTS}
        url = f"https://www.chevrolet.com/OCRestServices/dealer/latlong/v1/chevrolet/{lat}/{lng}"
        data = session.get(url, headers=headers, params=params, timeout=0.1).json()
        dealers = data.get("payload").get("dealers")
        return dealers or []
    except:
        if retry_count == 3:
            logger.info(f"Unable to fetch data for: {coord}")
            return []

        retry_count += 1
        return fetch_location(coord, retry_count)


def fetch_data():
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_radius_miles=MAX_DISTANCE,
        max_search_results=MAX_RESULTS,
    )
    search.initialize()

    locations = {}
    coord = search.next()

    while coord:
        coords = []
        dealers = fetch_location(coord)

        for dealer in dealers:
            store_number = dealer.get("id")
            if store_number in locations:
                continue

            data = extract(dealer)
            locations[store_number] = data
            coords.append([data.get("latitude"), data.get("longitude")])

            yield [data[field] for field in fields]

        search.update_with(coords)
        coord = search.next()

        logger.info(f"remaining zipcodes: {search.zipcodes_remaining()}")


def scrape():
    start = datetime.now()
    data = fetch_data()
    write_output(data)
    logger.info(f"duration: {datetime.now() - start}")


scrape()
