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


def get_driver(url, class_name, driver=None):
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

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
            break
        except Exception:
            driver.quit()
            if x == 10:
                raise Exception(
                    "Make sure this ran with a Proxy, will fail without one"
                )
            continue
    return driver


driver = get_driver("https://thedump.com/locations", "thedump-location-title")

soup = bs(driver.page_source, "html.parser")
grids = soup.find_all("div", attrs={"class": "col-md-4 thedump-location-block"})

for grid in grids:
    locator_domain = "theudmp.com"
    page_url = locator_domain + grid.find("h3").find("a")["href"]
    location_name = grid.find("h3").text.strip()

    address_part = grid.find(
        "div", attrs={"class": "thedump-location-address"}
    ).text.strip()
    if "Newport News" in address_part:
        address_pieces = address_part.split(",")[0].split(" ")
        address = ""
        for x in range(len(address_pieces) - 2):
            address = address + address_pieces[x] + " "

        city = address_pieces[-2] + " " + address_pieces[-1]
    else:
        address_pieces = address_part.split(",")[0].split(" ")
        address = ""
        for x in range(len(address_pieces) - 1):
            address = address + address_pieces[x] + " "

        city = address_pieces[-1]

    state = location_name.split(", ")[1]
    zipp = address_part.split(", ")[1].split(" ")[-1]
    country_code = "US"
    store_number = "<MISSING>"

    try:
        phone = (
            grid.find("div", attrs={"class": "thedump-location-phone"})
            .find("a")["href"]
            .replace("tel:", "")
        )
    except Exception:
        phone = "<MISSING>"

    if "warehouse" in location_name.lower():
        location_type = "Warehouse"
    else:
        location_type = "Store"

    lat_lon_url = grid.find_all("a")[-1]["href"]

    latitude = lat_lon_url.split("!3d")[1].split("!4d")[0]
    longitude = lat_lon_url.split("!4d")[1].split("?")[0]

    try:
        hours = (
            grid.text.strip()
            .split(phone[-4:])[1]
            .split("View on Map")[0]
            .replace("  ", " ")
            .replace("  ", " ")
            .strip()
        )
    except Exception:
        hours = (
            grid.text.strip()
            .split("Pickups Only")[1]
            .split("View on Map")[0]
            .replace("  ", " ")
            .replace("  ", " ")
            .strip()
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
