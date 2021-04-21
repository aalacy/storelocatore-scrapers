from sgrequests import SgRequests
import cloudscraper
import json
from bs4 import BeautifulSoup as bs
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
                    if (
                        "acceptsReservations"
                        in json.loads(html_string[start : end + 1]).keys()
                    ):
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

json_objects = extract_json(response)

for location in json_objects:
    locator_domain = "winkinglizard.com"
    address = location["address"]["streetAddress"].replace("\n", " ")
    city = location["address"]["addressLocality"]
    state = location["address"]["addressRegion"]
    zipp = location["address"]["postalCode"]
    country_code = "US"
    store_number = "<MISSING>"
    phone = location["address"]["telephone"]
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"

    hours = ""
    for item in location["openingHours"]:
        hours = hours + item + " "
    hours = hours[:-1]

    locator_domains.append(locator_domain)
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

soup = bs(response, "html.parser")
grids = soup.find_all("div", attrs={"class": "col-md-4 col-xs-12 pm-location"})

test_phones = []
for grid in grids:
    location_name = grid.find("h4").text.strip()
    page_url = (
        "https://www.winkinglizard.com"
        + grid.find("a", attrs={"class": "details-button"})["href"]
    )
    phone = grid.find_all("p")[1].find("a")["href"].replace("tel:", "")

    page_urls.append(page_url)
    location_names.append(location_name)
    test_phones.append(phone)

df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
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

df_name = pd.DataFrame(
    {"location_name": location_names, "page_url": page_urls, "phone": test_phones}
)

df = df.merge(df_name, left_on="phone", right_on="phone", how="outer")

df.to_csv("data.csv", index=False)
