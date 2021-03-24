from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import pandas as pd
import json


def parsedata(response_json, data_url):

    for location in response_json:
        try:
            location_name = location["name"]
        except Exception:
            continue

        locator_domain = "onemainfinancial.com"
        page_url = data_url
        location_name = location["name"]
        address = location["address"]["streetAddress"]
        city = location["address"]["addressLocality"]
        state = location["address"]["addressRegion"]
        zipp = location["address"]["postalCode"]
        country_code = "US"
        store_number = "<MISSING>"
        phone = location["telephone"]
        location_type = location["@type"]
        latitude = location["geo"]["latitude"]
        longitude = location["geo"]["longitude"]

        hours = ""
        for item in location["openingHours"]:
            hours = hours + item + ", "
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


def reset_sessions(data_url):

    s = SgRequests()

    driver = SgChrome().driver()
    driver.get(base_url)

    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = base_url + incap_str

    s.get(incap_url)

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                return [s, driver, headers, response_text]

        except Exception:
            continue


base_url = "https://onemainfinancial.com"

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

state_grab_url = "https://www.onemainfinancial.com/branches"

new_sess = reset_sessions(state_grab_url)

s = new_sess[0]
driver = new_sess[1]
headers = new_sess[2]
response_text = new_sess[3]

soup = bs(response_text, "html.parser")
li_bits = soup.find_all("li", attrs={"class": "col-sm-4 col-md-2"})

state_urls = [base_url + bit.find("a")["href"] for bit in li_bits]

location_urls = []
for url in state_urls:

    response = s.get(url, headers=headers)
    response_text = response.text
    if len(response_text.split("div")) > 2:
        pass
    else:
        new_sess = reset_sessions(state_grab_url)

        s = new_sess[0]
        driver = new_sess[1]
        headers = new_sess[2]
        response_text = new_sess[3]

    soup = bs(response_text, "html.parser")
    li_bits = soup.find_all("li", attrs={"class": "col-sm-4 col-md-2"})

    for bit in li_bits:
        location_url = base_url + bit.find("a")["href"]
        location_urls.append(location_url)

y = 0
for loc_url in location_urls:
    y = y + 1

    response = s.get(loc_url, headers=headers)
    response_text = response.text
    if len(response_text.split("div")) > 2:
        pass
    else:
        new_sess = reset_sessions(state_grab_url)

        s = new_sess[0]
        driver = new_sess[1]
        headers = new_sess[2]
        response_text = new_sess[3]

    json_objects = extract_json(response_text)
    parsedata(json_objects, loc_url)

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
