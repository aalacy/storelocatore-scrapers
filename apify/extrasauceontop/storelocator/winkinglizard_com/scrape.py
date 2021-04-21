from sgrequests import SgRequests
import cloudscraper
import json
import pandas as pd


def extract_json(html_string, filters=True):
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
                    if (
                        "acceptsReservations"
                        in json.loads(html_string[start : end + 1]).keys()
                        and filters is True
                    ):
                        json_objects.append(json.loads(html_string[start : end + 1]))
                    elif filters is False:
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

url = "https://www.winkinglizard.com/locations"
response = scraper.get(url).text
all_json = extract_json(response, filters=False)

for location in all_json[1]["preloadQueries"][4]["data"]["restaurant"]["pageContent"][
    "sections"
][0]["locations"]:
    locator_domain = "winkinglizard.com"
    page_url = locator_domain + "/" + location["slug"]
    location_name = location["name"]
    address = location["streetAddress"].replace("\n", " ")
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
    for section in location["schemaHours"]:
        hours = hours + section + " "
    hours = hours[:-1]

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
