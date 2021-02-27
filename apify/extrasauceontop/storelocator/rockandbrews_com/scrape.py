from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
import pandas as pd
import re

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

with SgChrome(executable_path="chromedriver.exe") as driver:
    driver.get("https://www.rockandbrews.com/locations")
    html = driver.page_source
    soup = bs(html, "html.parser")

    grids = soup.find_all("div", attrs={"class": "col-md-4 col-xs-12 pm-location"})

    for grid in grids:
        locator_domain = "rockandbrews.com"
        phone = "<MISSING>"

        name = grid.find("h4").text
        address = grid.find("span").text

        full_address = grid.find("a").text
        city_state_zipp = full_address.replace(address, "").strip()

        city = city_state_zipp.split(", ")[0]
        state = city_state_zipp.split(", ")[1].split(" ")[0]
        zipp = city_state_zipp.split(", ")[1].split(" ")[1]

        if len(state) < 2:
            pass
        else:
            country_code = "US"

            store_number = "<MISSING>"

            location_type = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            hour = grid.find("div", attrs={"class": "hours"}).text

            location_url_format = name.replace(" ", "-").replace("&", "-and-")
            page_url = "https://www.rockandbrews.com/" + location_url_format

            driver.get(page_url)
            html = driver.page_source
            soup = bs(html, "html.parser")

            div = soup.find("div", attrs={"id": "location"})
            try:
                phone = div.find("a")["href"].replace("tel:", "")
            except Exception:
                phone = "<MISSING>"

            if bool(re.search("[a-zA-Z]", phone)):
                phone = "<MISSING>"

            locator_domains.append(locator_domain)
            page_urls.append(page_url)
            location_names.append(name)
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
            hours_of_operations.append(hour)


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

df.to_csv("data.csv")
