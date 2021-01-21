import csv
import json
from tenacity import retry, stop_after_attempt
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "IsoCode": "US",
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
    locator_domain = "riamoneytransfer.com"


session = SgRequests()


@retry(stop=stop_after_attempt(5))
def fetch(lat, lng):
    body = {
        "CountryTo": "US",
        "FindLocationType": "RMT",
        "Lat": "",
        "Latitude": lat,
        "Long": "",
        "Longitude": lng,
        "RequestCountry": "US",
        "RequiredPayoutAgents": False,
        "RequiredReceivingAgents": False,
        "RequiredReceivingAndPayoutAgents": False,
        "PayAgentId": None,
    }
    result = session.put(
        "https://riamoneytransfer.com/api/location/agent-locations",
        json=body,
        headers=headers,
    ).json()

    return result


def set_jwt_token_header(session):
    session.get("https://riamoneytransfer.com/us/en/ria-locator", headers=headers)
    result = session.get('https://riamoneytransfer.com/api/Authorization/session', headers=headers).json()

    headers['Authorization'] = f'{result["authToken"]["tokenType"]} {result["authToken"]["jwtToken"]}'

    session.get_session().cookies.set("TOKEN", json.dumps(result['authToken']))


def fetch_data():
    searched = []
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA], max_search_results=20)

    set_jwt_token_header(session)

    for lat, lng in search:
        try:
            coords = []
            locations = fetch(lat, lng)
            for location in locations:
                store_number = get(location, "locationId")
                if store_number in searched:
                    continue
                searched.append(store_number)

                poi = extract(location, store_number)
                coords.append([poi.get("latitude"), poi.get("longitude")])

                yield [poi[field] for field in FIELDS]

            search.mark_found(coords)

        except Exception as e:
            logger.error(f"error fetching data for {lat} {lng}: {e}")


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
