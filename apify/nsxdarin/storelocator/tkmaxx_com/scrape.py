import csv
import json
from tenacity import retry, stop_after_attempt
from sgzip.static import static_zipcode_list, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

logger = SgLogSetup().get_logger("tkmaxx_com")

FIELDS = [
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
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


MISSING = "<MISSING>"


def get(location, key):
    return location.get(key, MISSING) or MISSING


def extract(location, store_number):
    locator_domain = "tkmaxx.com"
    location_name = get(location, "displayName")
    page_url = (
        f'https://tkmaxx.com/{get(location, "url")}'
        if get(location, "url") != MISSING
        else MISSING
    )

    if "TK Maxx" in location_name:
        location_type = "TK Maxx"
    if "Homesense" in location_name:
        location_type = "Homesense"
    else:
        location_type = MISSING

    street_address = get(location, "line1")
    if get(location, "line2") != MISSING:
        street_address += f', {get(location, "line2")}'

    city = get(location, "town")
    postal = get(location, "postalCode")
    state = MISSING
    country_code = "GB"
    latitude = get(location, "latitude")
    longitude = get(location, "longitude")

    phone = get(location, "phone")

    openings = get(location, "openings")
    hours_of_operation = MISSING
    if openings != MISSING:
        hours = json.loads(openings).items()
        hours_of_operation = ','.join([f'{day}: {hour}' for day, hour in hours])

    return {
        "locator_domain": locator_domain,
        "page_url": page_url,
        "location_name": location_name,
        "store_number": store_number,
        "location_type": location_type,
        "street_address": street_address,
        "city": city,
        "zip": postal,
        "state": state,
        "country_code": country_code,
        "latitude": latitude,
        "longitude": longitude,
        "phone": phone,
        "hours_of_operation": hours_of_operation,
    }


session = SgRequests()


@retry(stop=stop_after_attempt(5))
def fetch(postal):
    params = {"q": postal}
    result = session.get(
        "https://www.tkmaxx.com/uk/en/store-finder", params=params, headers=headers
    ).json()

    return result.get("data", [])


def fetch_data():
    searched = []
    search = static_zipcode_list(20, SearchableCountries.BRITAIN)

    session.get('https://www.tkmaxx.com', headers=headers)
    for postal in search:
        try:
            coords = []
            locations = fetch(postal)
            for location in locations:
                store_number = get(location, "name")
                if store_number in searched:
                    continue
                searched.append(store_number)

                poi = extract(location, store_number)
                coords.append([poi.get("latitude"), poi.get("longitude")])

                yield [poi[field] for field in FIELDS]

        except Exception as e:
            logger.error(f'error fetching data for {postal}: {e}')


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
