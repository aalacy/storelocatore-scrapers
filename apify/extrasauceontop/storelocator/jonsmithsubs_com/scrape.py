from sgrequests import SgRequests
import cloudscraper
import json
import pandas as pd


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

scraper = cloudscraper.create_scraper(sess=session)

base_url = "https://www.jonsmithsubs.com/locations"
response = scraper.get(base_url).text
response_text = response.replace("\n", "")


json_objects = extract_json(response_text)
with open("file.txt", "w", encoding="utf-8") as output:
    json.dump(
        json_objects[1]["preloadQueries"][4]["data"]["restaurant"]["pageContent"][
            "sections"
        ][2]["sectionColumns"],
        output,
        indent=2,
    )

for location in json_objects[1]["preloadQueries"][4]["data"]["restaurant"][
    "pageContent"
]["sections"][1]["locations"]:
    locator_domain = "jonsmithsubs.com"
    page_url = base_url

    location_name = location["name"]
    address = location["streetAddress"]
    city = location["city"]
    state = location["state"]
    zipp = location["postalCode"]
    country_code = location["country"]
    store_number = location["id"]
    phone = location["phone"]
    location_type = "<MISSING>"
    latitude = location["lat"]
    longitude = location["lng"]

    hours = ""
    try:
        for item in location["schemaHours"]:
            hours = hours + item + ", "

        hours = hours[:-2]
    except Exception:
        hours = "Opening Soon"

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

for location in json_objects[1]["preloadQueries"][4]["data"]["restaurant"][
    "pageContent"
]["sections"][2]["sectionColumns"]:
    locator_domain = "jonsmithsubs.com"
    page_url = base_url

    location_name = location["columnHeading"]
    address = location["columnContent"].split("\n")[0]
    city = location["columnContent"].split("\n")[1].split(",")[0]
    state = location["columnContent"].split("\n")[1].split(",")[1].strip().split(" ")[0]
    zipp = location["columnContent"].split("\n")[1].split(",")[1].strip().split(" ")[1]
    country_code = "US"
    store_number = location["id"]
    phone = location["columnContent"].split("\n")[-1]

    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours = "<MISSING>"

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
    hours_of_operations.append(hours)
    store_numbers.append(store_number)

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
