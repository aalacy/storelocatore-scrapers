from sgrequests import SgRequests
import cloudscraper
import json
import pandas as pd
from bs4 import BeautifulSoup as bs


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

base_url = "https://www.110grill.com"
response = scraper.get(base_url).text

json_objects = extract_json(response)

locations = json_objects[1]["preloadQueries"][0]["data"]["restaurant"]["homePage"][
    "sections"
][3]["locations"]

for location in locations:
    locator_domain = "110grill.com"
    try:
        page_url = (
            base_url
            + bs(
                location["customLocationContent"].replace("\t", "").replace("\n", ""),
                "html.parser",
            ).find("a")["href"]
        )
    except Exception:
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
