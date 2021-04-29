from sgrequests import SgRequests
import pandas as pd
import json


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
url = "https://maps.stores.claires.com/api/getAsyncLocations?template=search&level=search&search=27609&limit=10000&radius=1000000000"

response = session.get(url).json()

map_json = extract_json(response["maplist"])

for location in map_json:
    locator_domain = "claires.com"
    page_url = location["url"]
    location_name = location["location_name"]
    address = location["address_1"] + " " + location["address_2"]
    address = address.strip()
    city = location["city"]
    state = location["region"]
    zipp = location["post_code"]

    country_code = location["country"]
    if country_code not in ["US", "GB", "CA"]:
        continue

    store_number = location["lid"]
    phone = location["local_phone"]
    location_type = location["location_type"]
    latitude = location["lat"]
    longitude = location["lng"]

    if location["location_closure_message"] == "":
        try:
            hours_section = extract_json(location["hours_sets:primary"])[0]["days"]
            days = hours_section.keys()

            hours = ""
            for day in days:
                try:
                    start_time = hours_section[day][0]["open"]
                    end_time = hours_section[day][0]["close"]

                    hours = hours + day + " " + start_time + "-" + end_time + ", "

                except Exception:
                    hours = hours + day + " " + hours_section[day] + ", "

            hours = hours[:-2]
        except Exception:
            hours = "closed"
    else:
        hours = location["location_closure_message"]

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
