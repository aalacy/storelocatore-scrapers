import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgpostal import International_Parser, parse_address

from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt

logger = SgLogSetup().get_logger("tdbank_com")

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
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(FIELDS)

        # Body
        for row in data:
            writer.writerow(row)


@retry(stop=stop_after_attempt(3))
def fetch_country_locations(country, session):
    params = {
        "longitude": -78.5547283,
        "latitude": 35.8774409,
        "country": country,
        "locationtypes": 3,
        "json": "y",
        "searchradius": 2000,
        "searchunit": "mi",
        "numresults": 2000,
    }
    url = "https://www.tdbank.com/net/get12.ashx"
    response = session.get(url, 120, params=params).json()
    return response["markers"]["marker"]


MISSING = "<MISSING>"


def get(obj, key, default=MISSING):
    value = obj.get(key, default)
    return value if value else default


def get_name(page_url, session):
    try:
        response = session.get(page_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        return soup.find("h1", id="location-name").text
    except Exception as e:
        logger.error(e)
        return MISSING


def extract(location, session):
    locator_domain = "tdbank.com"
    store_number = get(location, "id")

    page_url = f"https://locations.td.com/{store_number}"
    location_type = get(location, "type")
    location_name = get_name(page_url, session)

    parsed = parse_address(International_Parser(), location["address"])
    street_address = parsed.street_address_1 or MISSING
    city = parsed.city or MISSING
    state = parsed.state or MISSING
    postal = parsed.postcode or MISSING

    country_code = get(location, "coun").upper()
    phone = get(location, "phoneNo")

    lat = get(location, "lat")
    lng = get(location, "lng")

    hours_of_operation = [
        f"{day}: {time}" for day, time in get(location, "hours", {}).items()
    ]
    hours_of_operation = (
        ",".join(hours_of_operation) if len(hours_of_operation) else MISSING
    )

    poi = {
        "locator_domain": locator_domain,
        "store_number": store_number,
        "page_url": page_url,
        "location_name": location_name,
        "location_type": location_type,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip": postal,
        "country_code": country_code,
        "latitude": lat,
        "longitude": lng,
        "phone": phone,
        "hours_of_operation": hours_of_operation,
    }
    return [poi[field] for field in FIELDS]


def fetch_data():
    # Your scraper here
    session = SgRequests()
    locations = []
    locations.extend(fetch_country_locations("US", session))
    locations.extend(fetch_country_locations("CA", session))

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(extract, location, session) for location in locations
        ]

        for future in as_completed(futures):
            poi = future.result()
            yield poi


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
