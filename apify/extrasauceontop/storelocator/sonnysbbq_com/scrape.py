from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import json
from bs4 import BeautifulSoup as bs
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


def get_driver(url, driver=None):
    if driver is not None:
        driver.quit()

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    x = 0
    while True:
        x = x + 1
        try:
            driver = SgChrome(
                executable_path=ChromeDriverManager().install(),
                user_agent=user_agent,
                is_headless=True,
            ).driver()
            driver.get(url)

            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


class_name = "location-view"
url = "https://api.sonnysbbq.com/api/v1/locations.bystate"
driver = get_driver(url)

soup = bs(driver.page_source, "html.parser")
object_response = soup.find("body").text.strip()

response = json.loads(object_response)
search_states = response.keys()

for search_state in search_states:
    for location in response[search_state]:
        locator_domain = "sonnysbbq.com"
        page_url = "https://www.sonnysbbq.com/locations/" + location[
            "post_title"
        ].lower().replace(".", "").replace(" - ", " ").replace(" ", "-").replace(
            ",", ""
        )
        location_name = location["post_title"]

        if len(location["acf"]["address"]["address"].split(",")) < 3:
            address_parts = location["acf"]["address"]["address"].replace(",", "")
            address_parts = address_parts.split(" ")[:-3]
            address = ""
            for part in address_parts:
                address = address + part + " "

            address = address[:-1]

            city = address_parts = location["acf"]["address"]["address"].split(" ")[-3]
            state = address_parts = location["acf"]["address"]["address"].split(" ")[-2]
            zipp = address_parts = location["acf"]["address"]["address"].split(" ")[-1]

        else:
            address = location["acf"]["address"]["address"].split(", ")[0]
            city = location["acf"]["address"]["address"].split(", ")[1]
            try:
                state = location["acf"]["address"]["address"].split(", ")[2]
                zipp = location["acf"]["address"]["address"].split(", ")[3]

            except Exception:
                state = (
                    location["acf"]["address"]["address"].split(", ")[2].split(" ")[0]
                )
                zipp = (
                    location["acf"]["address"]["address"].split(", ")[2].split(" ")[1]
                )

            if len(state.split(" ")) == 2:
                zipp = state.split(" ")[1]
                state = state.split(" ")[0]

        if zipp == "United States":
            zipp = "<MISSING>"

        country_code = "US"
        store_number = location["id"]
        phone = location["catering_phone_number"]
        if phone == "":
            phone = location["contact_phone"]
        location_type = "<MISSING>"
        latitude = location["address"]["lat"]
        longitude = location["address"]["lng"]

        hours = (
            location["store_hours"]
            .replace("Open for dine-in, takeout & delivery:<br />\r\n<br />\r\n", "")
            .replace("<br />\r\n", ", ")
            .replace("Open for dine-in, takeout and delivery:, , ", "")
            .replace("Open for dine-in, takeout or delivery:, , ", "")
        )

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
