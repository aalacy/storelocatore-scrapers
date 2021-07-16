from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

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

for search_code in search:
    url = (
        "https://photos3.walmart.com/store-finder/nearest-stores.json?address="
        + str(search_code)
        + "&limit=20"
    )

    response = session.get(url).json()

    for location in response["locations"]:
        locator_domain = "photos3.walmart.com"
        page_url = location["detailsPageURL"]
        location_name = location["displayName"]
        address = location["address"]["street"]
        city = location["address"]["city"]
        state = location["address"]["state"]
        zipp = location["address"]["zipcode"]
        country_code = location["address"]["country"]
        store_number = location["id"]

        try:
            phone = location["servicesMap"]["PHOTO_CENTER"]["phone"]

        except Exception:
            phone = location["phone"]

        location_type = location["storeType"]
        latitude = location["coordinates"]["latitude"]
        longitude = location["coordinates"]["longitude"]
        search.found_location_at(latitude, longitude)
        hours = ""
        for day in location["servicesMap"]["PHOTO_CENTER"]["operationalHours"].keys():
            try:
                open_time = location["servicesMap"]["PHOTO_CENTER"]["operationalHours"][
                    day
                ]["startHr"]
                close = location["servicesMap"]["PHOTO_CENTER"]["operationalHours"][
                    day
                ]["endHr"]
                hours = (
                    hours
                    + day.replace("Hrs", "")
                    + " "
                    + open_time
                    + "-"
                    + close
                    + ", "
                )

            except Exception:
                hours = hours + day.replace("Hrs", "") + " " + "closed" + ", "

        hours = hours[:-2]

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
