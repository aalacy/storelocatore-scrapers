from sgrequests import SgRequests
from sgselenium import SgChrome
import json
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(country_codes=[SearchableCountries.USA], max_radius_miles=100)

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


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


data_url = "https://www.biscuitville.com"

driver = SgChrome(is_headless=True).driver()
driver.get(data_url)

s = SgRequests()
headers = driver.requests[3].headers
response = s.get(data_url, headers=headers, allow_redirects=True).text

json_objects = extract_json(response)

for item in json_objects:
    if "nonce" in item.keys():
        nonce = item["nonce"]

base_url = "https://biscuitville.com/wp-admin/admin-ajax.php"

for search_lat, search_lng in search:
    params = {
        "action": "get_dl_locations",
        "all": "false",
        "radius": "100",
        "lat": search_lat,
        "lng": search_lng,
        "current_location": "N",
        "nonce": nonce,
    }

    data = s.post(base_url, data=params, headers=headers).json()

    with open("file.txt", "w", encoding="utf-8") as output:
        json.dump(data, output, indent=4)

    data_states = data["locations"].keys()
    for data_state in data_states:
        if data_state == "SOON":
            continue
        data_states_dict = data["locations"][data_state]
        data_cities = data_states_dict.keys()
        for data_city in data_cities:
            for location in data_states_dict[data_city]:
                locator_domain = "biscuitville.com"
                page_url = location["location_url"]
                location_name = location["name"]
                address = location["address"]
                city = location["city"]
                state = location["state"]
                zipp = location["zip"]
                country_code = "US"
                store_number = location["id"]
                phone = location["phone"]
                location_type = location["service_type"]
                latitude = location["lat"]
                longitude = location["lng"]
                hours = (
                    location["details"]
                    .replace(" \r\n", ", ")
                    .replace("\n", ", ")
                    .replace("\r", "")
                )
                hours = hours.split(", ,")[0]

                locator_domains.append(locator_domain)
                page_urls.append(page_url)
                location_names.append(location_name)
                street_addresses.append(address)
                citys.append(city)
                states.append(state)
                zips.append(zipp)
                country_codes.append(country_code)
                phones.append(phone)
                location_types.append(location_type)
                latitudes.append(latitude)
                longitudes.append(longitude)
                store_numbers.append(store_number)
                hours_of_operations.append(hours)

                search.found_location_at(latitude, longitude)

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
        "country_code": country_codes,
        "location_type": location_types,
        "hours_of_operation": hours_of_operations,
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
