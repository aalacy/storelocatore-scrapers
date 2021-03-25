from sgselenium import SgChrome
from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_radius_miles=1000,
    max_search_results=100,
)

initial_search_url = "https://prismahealth.org/api/search/search?pageSize=100&pageNumber=1&searchType=location"

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
unique_names = []


def parsedata(response_json, data_url):
    locations = response_json["Items"]
    coords = []
    for location in locations:
        locator_domain = "prismahealth.org"
        page_url = data_url
        location_name = location["Title"]

        address = location["Address"][0]

        city = location["Address"][2].split(",")[0]
        state = location["Address"][2].split(" ")[-2]
        zipp = city = location["Address"][2].split(" ")[-1]

        country_code = "US"
        store_number = location["Id"].split(";")[0]

        phone = location["Phone"]
        location_type = "<MISSING>"
        latitude = location["Coordinate"]["Latitude"]
        longitude = location["Coordinate"]["Longitude"]

        hours = "<MISSING>"

        locator_domains.append(locator_domain)
        page_urls.append(page_url)

        location_names.append(location_name)
        if location_name not in location_names:
            unique_names.append(location_name)
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

        current_coords = [latitude, longitude]
        coords.append(current_coords)
    search.mark_found(coords)


base_url = "https://prismahealth.org"

s = SgRequests()

driver = SgChrome().driver()
driver.get(base_url)

incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
incap_url = base_url + incap_str

s.get(incap_url)

for request in driver.requests:
    initial_search_url = "https://prismahealth.org/api/search/search?pageSize=100&pageNumber=1&searchType=location"

    headers = request.headers
    if headers["Host"] == "prismahealth.org":
        try:
            response = s.get(initial_search_url, headers=headers)
            response_text = response.text
            response_json = response.json()
            total_results = int(response_json["NumOfResults"])

            break

        except Exception:
            continue


def reset_sessions(zipcode):
    base_url = "https://prismahealth.org"
    s = SgRequests()

    driver = SgChrome().driver()
    driver.get(base_url)

    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = base_url + incap_str

    s.get(incap_url)

    for request in driver.requests:
        data_url = (
            "https://prismahealth.org/api/search/search?pageSize=100&pageNumber=1&searchType=location&zip="
            + zipcode
            + "&radius=100"
        )

        headers = request.headers
        if headers["Host"] == "prismahealth.org":
            try:
                response = s.get(data_url, headers=headers)
                response_json = response.json()
                break

            except Exception:
                continue

            parsedata(response_json, data_url)

    return [s, driver]


x = 0

for zipcode in search:

    x = x + 1
    success = 0
    count = 0

    for request in driver.requests:
        data_url = (
            "https://prismahealth.org/api/search/search?pageSize=100&pageNumber=1&searchType=location&zip="
            + zipcode
            + "&radius=1000"
        )

        headers = request.headers

        if headers["Host"] == "prismahealth.org":
            count = count + 1

            try:
                response = s.get(data_url, headers=headers)
                response_json = response.json()

                success = 1

            except Exception:
                if count == 5:
                    break
                continue

            parsedata(response_json, data_url)
            break

    if success == 0:
        new_sessions = reset_sessions(zipcode)
        s = new_sessions[0]
        driver = new_sessions[1]

    if len(unique_names) == total_results:
        break

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

df.to_csv("data.csv", index=True)
