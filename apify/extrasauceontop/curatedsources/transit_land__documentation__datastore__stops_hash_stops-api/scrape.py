from sgrequests import SgRequests
import pandas as pd
import time

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

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "content-type": "application/json",
    "origin": "https://www.transit.land",
    "referer": "https://www.transit.land/",
}
session = SgRequests(retry_behavior=False)
x = 0

onestop_ids = []
while True:
    params = {
        "operationName": "",
        "variables": {"search": "", "merged": False, "limit": 1000, "after": x},
        "query": "query ($limit: Int, $after: Int, $search: String, $merged: Boolean) {\n  entities: operators(\n    after: $after\n    limit: $limit\n    where: {search: $search, merged: $merged}\n  ) {\n    id\n    agency_name\n    operator_name\n    operator_short_name\n    onestop_id\n    city_name\n    adm1name\n    adm0name\n    places_cache\n    agency {\n      places(where: {min_rank: 0.2}) {\n        name\n        adm0name\n        adm1name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
    }

    url = "https://demo.transit.land/api/v2/query"
    response = session.post(url, json=params, headers=headers).json()

    if len(response["data"]["entities"]) == 0:
        break

    for location in response["data"]["entities"]:
        if (
            location["adm0name"] == "United States of America"
            or location["adm0name"] == "Ireland"
            or location["adm0name"] == "United Kingdom"
            or location["adm0name"] == "Canada"
        ):
            onestop_ids.append(location["onestop_id"])

    x = x + 1000

x = 0
api_keys = [
    "js3Mzn9chq5ZCMWiJCn2rcE86pJSE7Kt",
    "LZplP41M9JQ0tJq2obNgMoGIs4sgaERl",
    "mf5aDbbRmWv6tHZeu73zGz9yWX1sQ0WR",
]
for onestop_id in onestop_ids:
    offset = 0
    x = x + 1

    api_key = api_keys[x % 3]
    while True:

        y = 0
        while True:
            y = y + 1
            if y == 11:
                break
            try:
                url = (
                    "https://api.transit.land/api/v1/stops?apikey="
                    + api_key
                    + "&offset="
                    + str(offset)
                    + "&per_page=500&sort_key=id&sort_order=asc&served_by="
                    + onestop_id
                )
                response = session.get(url, timeout=1000)
                response_code = response.status_code
                response = response.json()
                break
            except Exception:
                continue

        if response_code == 404:
            time.sleep(0.5)
        try:
            if len(response["stops"]) == 0:
                break
        except Exception:
            break

        for location in response["stops"]:
            locator_domain = (
                "https://www.transit.land/documentation/datastore/stops#stops-api"
            )
            try:
                page_url = location["tags"]["stop_url"]

            except Exception:
                page_url = "<MISSING>"

            location_name = (
                location["operators_serving_stop"][0]["operator_name"]
                + "-"
                + location["name"]
            )
            address = location["name"]
            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "<MISSING>"
            latitude = location["geometry"]["coordinates"][1]
            longitude = location["geometry"]["coordinates"][0]
            store_number = (
                location["operators_serving_stop"][0]["operator_name"]
                + "_"
                + location["onestop_id"]
            )
            hours = "<MISSING>"
            phone = "<MISSING>"
            location_type_parts = location["served_by_vehicle_types"]

            location_type = ""
            for part in location_type_parts:
                location_type = location_type + str(part) + ","

            location_type = location_type[:-1]

            locator_domains.append(locator_domain)
            page_urls.append(page_url)
            location_names.append(location_name)
            street_addresses.append(address)
            citys.append(city)
            states.append(state)
            zips.append(zipp)
            country_codes.append(country_code)
            store_numbers.append(store_number)
            phones.append(phone)
            location_types.append(location_type)
            latitudes.append(latitude)
            longitudes.append(longitude)
            hours_of_operations.append(hours)

        if len(response["stops"]) < 500:
            break

        else:
            offset = offset + 500

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
