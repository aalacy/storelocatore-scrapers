import os

os.system("pip uninstall -y sgselenium")
os.system("pip install sgselenium==0.1.1")

from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager


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

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
with SgChrome(
    executable_path=ChromeDriverManager().install(),
    user_agent=user_agent,
    is_headless=True,
).driver() as driver:
    driver.get("https://www.metro.ca/en/find-a-grocery")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "hero--small"))
    )
    soup = bs(driver.page_source, "html.parser")

locations = soup.find_all("li", attrs={"class": "fs--box-shop"})

for location in locations:
    locator_domain = "metro.ca"
    page_url = "https://www.metro.ca" + location.find("a")["href"]
    location_name = location["data-store-name"]
    address = (
        location.find("div", attrs={"class": "address--line1"})
        .find("span")
        .text.strip()
    )
    city = location.find("span", attrs={"class": "address--city"}).text.strip()
    state = location.find("span", attrs={"class": "address--provinceCode"}).text.strip()
    zipp = location.find("span", attrs={"class": "address--postalCode"}).text.strip()
    country_code = "CA"
    store_number = location["data-store-id"]
    phone = (
        location.find("div", attrs={"class": "store-phone"})
        .find("span")
        .text.strip()
        .split("/")[0]
    )
    location_type = "<MISSING>"
    latitude = location["data-store-lat"]
    longitude = location["data-store-lng"]

    hours = "<INACCESSIBLE>"

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

driver.quit()

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
