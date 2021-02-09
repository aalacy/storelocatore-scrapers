import csv
import json
from tenacity import retry, stop_after_attempt

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "IsoCode": "",
    "CultureCode": "en-US",
    "Current-Page": "https://riamoneytransfer.com/us/en/ria-locator",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json;charset=utf-8",
}

logger = SgLogSetup().get_logger("riamoneytransfer_com")

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
        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


MISSING = "<MISSING>"


def get(location, key):
    return location.get(key, MISSING) or MISSING


def extract(location, store_number, country):
    locator_domain = "riamoneytransfer.com"
    page_url = MISSING
    location_name = get(location, "name")
    street_address = get(location, "address")
    city = get(location, "city")
    state = get(location, "state")
    zip = MISSING
    country_code = country
    store_number = get(location, "locationId")
    phone = get(location, "phone")
    location_type = get(location, "locationType")
    latitude = get(location, "latitude")
    longitude = get(location, "longitude")
    hours_of_operation = []
    for elem in location["businessHours"]:
        day = elem["dayOfWeek"]
        opens = elem["timeOpen"]
        closes = elem["timeClose"]
        hours_of_operation.append(f"{day} {opens} - {closes}")
    hours_of_operation = " ".join(hours_of_operation)
    if hours_of_operation == "0 None - None":
        hours_of_operation = "<MISSING>"

    data = {
        "locator_domain": locator_domain,
        "page_url": page_url,
        "location_name": location_name,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip": zip,
        "country_code": country_code,
        "store_number": store_number,
        "phone": phone,
        "location_type": location_type,
        "latitude": latitude,
        "longitude": longitude,
        "hours_of_operation": hours_of_operation,
    }
    return data


@retry(stop=stop_after_attempt(5))
def fetch(lat, lng, country):
    body = {
        "CountryTo": country,
        "FindLocationType": "RMT",
        "Lat": "",
        "Latitude": lat,
        "Long": "",
        "Longitude": lng,
        "RequestCountry": country,
        "RequiredPayoutAgents": False,
        "RequiredReceivingAgents": False,
        "RequiredReceivingAndPayoutAgents": False,
        "PayAgentId": None,
    }
    new_headers = headers
    new_headers["IsoCode"] = country
    result = session.put(
        "https://riamoneytransfer.com/api/location/agent-locations",
        json=body,
        headers=new_headers,
    ).json()
    return result


def set_jwt_token_header(session):
    session.get("https://riamoneytransfer.com/us/en/ria-locator", headers=headers)
    result = session.get(
        "https://riamoneytransfer.com/api/Authorization/session", headers=headers
    ).json()

    headers[
        "Authorization"
    ] = f'{result["authToken"]["tokenType"]} {result["authToken"]["jwtToken"]}'

    session.get_session().cookies.set("TOKEN", json.dumps(result["authToken"]))


def fetch_data():
    searched = []
    all_coordinates = {}
    us_search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], max_radius_miles=50
    )
    ca_search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], max_radius_miles=50
    )
    uk_search = DynamicGeoSearch(
        country_codes=[SearchableCountries.BRITAIN], max_radius_miles=50
    )
    all_coordinates = {"CA": ca_search, "UK": uk_search, "US": us_search}

    for country, coordinates in all_coordinates.items():
        set_jwt_token_header(session)
        coords = []
        for lat, lng in coordinates:
            try:
                locations = fetch(lat, lng, country)
            except Exception as e:
                logger.error(f"error fetching data for {lat} {lng}: {e}")
                continue
            if len(locations) == 1:
                set_jwt_token_header(session)
            print(country, len(locations))
            for location in locations:
                if type(location) == str:
                    continue
                loc_id = get(location, "locationId")
                check = f"{country} {loc_id}"
                if check in searched:
                    continue
                searched.append(loc_id)

                poi = extract(location, loc_id, country)
                if not poi:
                    continue
                coords.append([poi.get("latitude"), poi.get("longitude")])

                yield [poi[field] for field in FIELDS]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
