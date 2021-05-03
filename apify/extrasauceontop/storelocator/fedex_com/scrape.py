from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

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

session = SgRequests()

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA], max_search_results=75
)

for search_lat, search_lon in search:
    data_url = (
        "https://local.fedex.com/search-results/"
        + str(search_lat)
        + ","
        + str(search_lon)
        + "/?ajax=true&group_filters[]=office_group&filters[]=fedex&show=50"
    )
    data_response = session.get(data_url).json()

    for location in data_response["results"]:
        locator_domain = "fedex.com"

        try:
            page_url = "https://local.fedex.com/" + location["location_url"]
        except Exception:
            page_url = "<MISSING>"

        location_name = location["e_disp_nm"]
        address = location["address"]
        city = location["city"]
        state = location["state"]
        zipp = location["postalcode"]
        country_code = location["country_cd"]
        latitude = location["latitude"]
        longitude = location["longitude"]
        search.found_location_at(latitude, longitude)
        if country_code != "US":
            continue
        store_number = location["locid"]
        if store_number in store_numbers:
            continue

        phone = location["stor_phone_digit"]

        location_type = location["location_type"]
        if location_type == "fedex":
            location_type = "Ship Center"
        else:
            location_type = "Office Store"

        hours_data = session.get(page_url).text
        hours_soup = bs(hours_data, "html.parser")
        hours_parts = hours_soup.find_all("meta", attrs={"itemprop": "openingHours"})
        hours = ""
        for part in hours_parts:
            hours = hours + part["content"] + ", "
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
