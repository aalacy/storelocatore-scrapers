from sgrequests import SgRequests
import json
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import pandas as pd

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

search = DynamicZipSearch(country_codes=[SearchableCountries.USA])

session = SgRequests()

headers = {
    "User-Agent": "PostmanRuntime/7.19.0",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}
session = SgRequests()
url = "https://www.picknsave.com/stores/api/graphql"

data = {
    "query": "\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n",
    "variables": {"searchText": "39702", "filters": []},
    "operationName": "storeSearch",
}


def get_session(data):
    while True:
        try:
            session = SgRequests(retry_behavior=None)
            response = session.post(url, json=data, headers=headers, timeout=3).json()

            if response["data"]["storeSearch"]["fuel"] is None:
                continue
            return [session, response]
        except Exception:
            continue


x = 0
for zipcode in search:
    coords = []
    data = {
        "query": "\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n",
        "variables": {"searchText": zipcode, "filters": []},
        "operationName": "storeSearch",
    }
    if x == 0:
        session_response = get_session(data)
        session = session_response[0]
        response = session_response[1]

    else:
        try:
            response = session.post(url, json=data, headers=headers, timeout=3).json()
            if response["data"]["storeSearch"]["fuel"] is None:
                session_response = get_session(data)
                session = session_response[0]
                response = session_response[1]
        except Exception:
            session_response = get_session(data)
            session = session_response[0]
            response = session_response[1]

    for item in response["data"]["storeSearch"]["fuel"]:

        locator_domain = "picknsave.com"
        page_url = url
        location_name = item["vanityName"]
        address = item["address"]["addressLine1"]
        city = item["address"]["city"]
        state = item["address"]["stateCode"]
        country = item["address"]["countryCode"]
        zipp = item["address"]["zip"]
        store_number = item["storeNumber"]
        phone = item["phoneNumber"]
        location_type = item["banner"]
        latitude = item["latitude"]
        longitude = item["longitude"]
        hour_string = ""
        for day_hours in item["ungroupedFormattedHours"]:
            day = day_hours["displayName"]
            hours = day_hours["displayHours"]

            hour_string = hour_string + day + ": " + hours + ", "

        locator_domains.append(locator_domain)
        page_urls.append(page_url)
        location_names.append(location_name)
        street_addresses.append(address)
        citys.append(city)
        states.append(state)
        country_codes.append(country)
        zips.append(zipp)
        store_numbers.append(store_number)
        location_types.append(location_type)
        latitudes.append(latitude)
        longitudes.append(longitude)
        hours_of_operations.append(hour_string)
        phones.append(phone)

        coords.append([latitude, longitude])

    for item in response["data"]["storeSearch"]["stores"]:

        locator_domain = "picknsave.com"
        page_url = url
        location_name = item["vanityName"]
        address = item["address"]["addressLine1"]
        city = item["address"]["city"]
        state = item["address"]["stateCode"]
        country = item["address"]["countryCode"]
        zipp = item["address"]["zip"]
        store_number = item["storeNumber"]
        phone = item["phoneNumber"]
        location_type = item["banner"]
        latitude = item["latitude"]
        longitude = item["longitude"]
        hour_string = ""
        for day_hours in item["ungroupedFormattedHours"]:
            day = day_hours["displayName"]
            hours = day_hours["displayHours"]

            hour_string = hour_string + day + ": " + hours + ", "

        locator_domains.append(locator_domain)
        page_urls.append(page_url)
        location_names.append(location_name)
        street_addresses.append(address)
        citys.append(city)
        states.append(state)
        country_codes.append(country)
        zips.append(zipp)
        store_numbers.append(store_number)
        location_types.append(location_type)
        latitudes.append(latitude)
        longitudes.append(longitude)
        hours_of_operations.append(hour_string)
        phones.append(phone)

        coords.append([latitude, longitude])

    deduped_coords = []
    for item in coords:
        if item not in deduped_coords:
            deduped_coords.append(item)
    search.mark_found(coords)
    x = x + 1


df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_of_operations,
        "country_code": country_codes,
        "location_type": location_types,
    }
)

df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)
