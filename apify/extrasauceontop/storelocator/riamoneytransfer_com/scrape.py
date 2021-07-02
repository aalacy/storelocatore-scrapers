import json
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed
from sgzip.static import static_coordinate_list, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
import re
import pandas as pd

session = SgRequests()

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

    df = pd.DataFrame(columns=FIELDS)

    for row in data:
        df2 = pd.DataFrame(row)
        df = df.append(df2)

        df = df.fillna("<MISSING>")
        df = df.replace(r"^\s*$", "<MISSING>", regex=True)

        df["dupecheck"] = (
            df["location_name"].map(str)
            + df["street_address"].map(str)
            + df["city"].map(str)
            + df["state"].map(str)
            + df["location_type"].map(str)
            + df["store_number"].map(str)
        )

        df = df.drop_duplicates(subset=["dupecheck"])
        df = df.drop(columns=["dupecheck"])

        df.to_csv("data.csv", index=False)


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
    phone = re.sub("[^0-9]", "", phone)
    if phone == "":
        phone = "<MISSING>"

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


def scrape_loc_urls(country, coordinates):
    count = 0
    results = []
    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(parallel_run, lat, lng, country) for lat, lng in coordinates
        ]
        for future in as_completed(futures):
            try:
                count += 1
                logger.info(f"{country}: {count}/{len(coordinates)}")
                record = future.result()
                if record:
                    for poi in record:
                        results.append(poi)
            except Exception:
                pass

    return results


SEARCH_RADIUS = 10


def fetch_data():
    all_coordinates = {}
    us_search = static_coordinate_list(
        radius=SEARCH_RADIUS, country_code=SearchableCountries.USA
    )
    ca_search = static_coordinate_list(
        radius=SEARCH_RADIUS, country_code=SearchableCountries.CANADA
    )
    uk_search = static_coordinate_list(
        radius=SEARCH_RADIUS, country_code=SearchableCountries.BRITAIN
    )
    all_coordinates = {"US": us_search, "CA": ca_search, "UK": uk_search}

    results = []
    for country, coordinates in all_coordinates.items():

        set_jwt_token_header(session)
        data = scrape_loc_urls(country, coordinates)
        results.append(data)

    return results


def parallel_run(lat, lng, country):
    pois = []
    try:
        locations = fetch(lat, lng, country)

        if len(locations) == 1:
            set_jwt_token_header(session)
        for location in locations:
            if type(location) == str:
                pass
            else:
                loc_id = get(location, "locationId")
                poi = extract(location, loc_id, country)
                if not poi:
                    pass
                else:
                    pois.append(poi)

    except Exception:
        return

    return pois


def scrape():
    start = dt.now()
    data = fetch_data()
    write_output(data)
    logger.info(f"duration: {dt.now() - start}")


scrape()
