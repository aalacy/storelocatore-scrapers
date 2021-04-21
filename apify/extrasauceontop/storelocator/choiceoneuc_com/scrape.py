from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
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

url = "https://www.umms.org/health-services/urgent-care/locations"
response = scraper.get(url).text

soup = bs(response, "html.parser")

loc_urls = [
    "https://www.umms.org" + a_tag["href"]
    for a_tag in soup.find("ul", attrs={"class": "nav-content__nested-level"}).find_all(
        "a"
    )
]

for url in loc_urls:

    response = scraper.get(url).text
    soup = bs(response, "html.parser")

    locator_domain = "www.umms.org"
    page_url = url

    json_objects = extract_json(response)

    location_name = soup.find(
        "h1", attrs={"class": "l-content-header__h1"}
    ).text.strip()
    address = json_objects[1]["items"][0]["address1"]
    city = json_objects[1]["items"][0]["address2"].split(",")[0]
    state = json_objects[1]["items"][0]["address2"].split(", ")[1].split(" ")[0]
    zipp = json_objects[1]["items"][0]["address2"].split(", ")[1].split(" ")[1][:5]
    country_code = "US"
    store_number = "<MISSING>"
    phone = json_objects[1]["items"][0]["phone"]
    location_type = "<MISSING>"
    latitude = json_objects[1]["items"][0]["coordinates"][0]["lat"]
    longitude = json_objects[1]["items"][0]["coordinates"][0]["lng"]

    hours = "Sun-Sat 8 am-8 pm"

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
