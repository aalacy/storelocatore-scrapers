from sgrequests import SgRequests
from sgselenium import SgChrome
import pandas as pd
from bs4 import BeautifulSoup as bs
import re


def reset_sessions(data_url):

    s = SgRequests()

    driver = SgChrome().driver()
    driver.get(data_url)

    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = data_url + incap_str

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

response = reset_sessions("https://mezeh.com/locations/")[-1]
soup = bs(response, "html.parser")

grids = soup.find_all(
    "div", attrs={"class": "column_attr clearfix align_left mobile_align_left"}
)
session = SgRequests()
for grid in grids:
    locator_domain = "mezeh.com"
    page_url = grid.find("a")["href"]
    location_name = grid.find("h4").text.strip()
    try:
        address_section = grid.find("a").text.strip().split("\n")[1]
        address_parts = address_section.split(".")
        if len(address_parts) > 1:
            address_parts = address_parts[:-1]
            address = ""
            for part in address_parts:
                address = address + part + " "
            address = address.strip()
        else:
            address_parts = address_parts[0].split(",")[0].split(" ")[:-1]
            address = ""
            for part in address_parts:
                address = address + part + " "
            address = address.strip()

        city = address_section.split(" ")[-3].replace(",", "").replace(".", "").strip()
        state = address_section.split(" ")[-2].replace(",", "").replace(".", "").strip()
        zipp = address_section.split(" ")[-1].replace(",", "").replace(".", "").strip()
        country_code = "US"
        store_number = "<MISSING>"

        phone = grid.text.split("phone")[1].split("hours")[0].replace("\n", "")
        hours_parts = grid.text.split("hours")[1].split("order")[0].split("\n")
        hours = ""
        for item in hours_parts:
            item = item.replace("\r", "")
            hours = hours + item + " "
        location_type = "<MISSING>"
        hours = hours.strip()

        latlon_url = grid.find("a", text=re.compile("get directions"))["href"]
        r = session.get(latlon_url).url
        latitude = r.split("@")[1].split(",")[0]
        longitude = r.split("@")[1].split(",")[1]

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

    except Exception as e:
        if "coming soon" in grid.text.strip():
            address_section = grid.find("h5").text.strip()
            address_parts = address_section.split("phone")[0].split(".")
            if len(address_parts) > 1:
                address_parts = address_parts[:-1]
                address = ""
                for part in address_parts:
                    address = address + part + " "
                address = address.strip()
            else:
                address_parts = address_parts[0].split(",")[0].split(" ")[:-1]
                address = ""
                for part in address_parts:
                    address = address + part + " "
                address = address.strip()

            city = (
                address_section.split(" ")[-3]
                .replace(",", "")
                .replace(".", "")
                .strip()
                .replace("blvd", "")
            )
            state = (
                address_section.split(" ")[-2].replace(",", "").replace(".", "").strip()
            )
            zipp = (
                address_section.split(" ")[-1]
                .replace(",", "")
                .replace(".", "")
                .strip()
                .split("\n")[0]
            )
            country_code = "US"
            store_number = "<MISSING>"

            if "phone" in grid.text.strip():
                phone = grid.text.strip().split("phone")[1].split("\n")[1]
            else:
                phone = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours = "Coming Soon"

        else:
            address = grid.find("h5").text.strip().split(".")[0]
            city = grid.find("h5").text.strip().split(".")[1].split(",")[0]
            state = (
                grid.find("h5").text.strip().split(".")[1].split(",")[1].split(" ")[1]
            )
            zipp = (
                grid.find("h5")
                .text.strip()
                .split(".")[1]
                .split(",")[1]
                .split(" ")[2]
                .split("\n")[0]
            )
            phone = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            hours = "Temporarily Closed"
            store_number = "<MISSING>"
            country_code = "US"

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
