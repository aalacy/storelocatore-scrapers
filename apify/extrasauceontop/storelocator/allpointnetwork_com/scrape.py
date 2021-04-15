from sgrequests import SgRequests
import json
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(
    country_codes=[
        SearchableCountries.USA,
        SearchableCountries.CANADA,
        SearchableCountries.BRITAIN,
    ],
    max_radius_miles=100,
)

session = SgRequests()

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

url = "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"

x = 0
for search_lat, search_lon in search:

    params = {
        "Latitude": str(search_lat),
        "Longitude": str(search_lon),
        "Miles": "100",
        "NetworkId": "10029",
        "SearchByOptions": "",
    }

    response = session.post(url, json=params).json()

    for location in response["data"]:
        locator_domain = "allpointnetwork.com"
        page_url = (
            "https://clsws.locatorsearch.net/Rest/LocatorSearchAPI.svc/GetLocations"
        )
        location_name = "Allpoint " + location["RetailOutlet"]
        address = location["Street"]
        city = location["City"]
        state = location["State"]
        zipp = location["ZipCode"]
        country_code = location["Country"]
        if country_code == "MX":
            continue
        store_number = location["LocationID"]
        phone = "<MISSING>"
        location_type = location["RetailOutlet"]
        latitude = location["Latitude"]
        longitude = location["Longitude"]
        search.found_location_at(latitude, longitude)
        hours = "<MISSING>"

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

    x = x + 1
    # if x == 10:
    #     break

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

df.to_csv("data.csv", index=False, encoding="utf-8")
