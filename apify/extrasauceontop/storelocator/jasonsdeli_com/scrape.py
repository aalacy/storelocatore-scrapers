from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import cloudscraper
import json
import html
import pandas as pd


def extract_json(html_string):
    json_objects = []
    count = 0

    html_string = html.unescape(html_string)
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
phones = []  #
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []  #

x = 0
while True:
    session = SgRequests()
    scraper = cloudscraper.create_scraper(sess=session)
    url = "https://www.jasonsdeli.com/restaurants"

    x = x + 1
    response = scraper.get(url).text
    json_objects = extract_json(response)

    if len(json_objects[0].keys()) == 0:
        continue
    else:
        break

for location in json_objects[0]["leaflet"][0]["features"][:-1]:
    locator_domain = "jasonsdeli.com"

    popup_text = location["popup"]
    popup_soup = bs(popup_text, "html.parser")

    page_url = "https://www.jasonsdeli.com" + popup_soup.find("a")["href"]
    location_name = popup_soup.find("strong").text.strip().split(": ")[1]
    address = (
        popup_soup.text.strip().split(location_name)[1].split("\n")[0].replace("\r", "")
    )

    city_state_parts = (
        popup_soup.find("strong")
        .text.strip()
        .replace(" : ", ": ")
        .split(": ")[0]
        .split(" ")
    )

    city = ""
    for part in city_state_parts[:-1]:
        city = city + part + " "
    city = city.strip().replace(",", "")

    state = city_state_parts[-1]
    if state == "Texas":
        state = "TX"

    zipp = popup_soup.text.strip().split(" ")[-1].strip()
    country_code = "US"

    store_number = location["feature_id"]
    location_type = "<MISSING>"

    latitude = location["lat"]
    longitude = location["lon"]

    location_response = scraper.get(page_url).text

    location_soup = bs(location_response, "html.parser")

    phone = location_soup.find("a", attrs={"class": "cnphone"}).text.strip()
    if phone == "":
        phone = "<MISSING>"

    hours_parts = location_soup.find("div", attrs={"class": "loc-hours"}).find_all("p")

    hours = ""
    for part in hours_parts:
        hours_text = part.text.strip()
        hours_text = html.unescape(hours_text)

        hours = hours + hours_text + ", "

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
