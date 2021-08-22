from sgrequests import SgRequests
import json
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


session = SgRequests()
url = "https://www.amitahealth.org/find-a-location/?page=1&count=5000"

response = session.get(url).text
json_objects = extract_json(response)
data = extract_json(json_objects[-1]["SettingsData"])
locations = extract_json(data[0]["EntityJsonData"])

for location in locations:
    locator_domain = "amitahealth.org"
    page_url = "https://www.amitahealth.org/location/" + location["DirectUrl"]

    if (
        page_url == "https://www.amitahealth.org/location/amita-health-medical-group"
        or page_url == "https://www.amitahealth.org/location/er-wait-times"
    ):
        continue

    location_name = location["Name"]

    if location_name == "Provider Locations":
        continue

    address = (location["Address1"] + " " + location["Address2"]).strip()
    city = location["City"]
    state = location["StateName"]
    zipp = location["PostalCode"]
    country_code = "US"
    store_number = location["Id"]
    phone = location["Phone"]
    location_type = location["OrgType"]
    latitude = location["Latitude"]
    longitude = location["Longitude"]

    hours_response = session.get(page_url).text

    hours_data = extract_json(hours_response)
    hours_data = extract_json(hours_data[5]["SettingsData"])

    hours_contenders = hours_data[0]["StaticPageZones"][0]["Value"]["FieldColumns"][2][
        "Fields"
    ]

    for item in hours_contenders:
        if item["PublicLabel"] == "Office Hours":
            hours_parts = item

    hours = ""
    for part in hours_parts["Values"]:
        hours = hours + part + ", "

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
