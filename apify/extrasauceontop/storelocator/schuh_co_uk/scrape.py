from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sgselenium.sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import pandas as pd
import ast

search = DynamicGeoSearch(country_codes=[SearchableCountries.BRITAIN])

locator_domains = []  #
page_urls = []  #
location_names = []  #
street_addresses = []  ###
citys = []  #
states = []
zips = []  #
country_codes = []  #
store_numbers = []  #
phones = []  #
location_types = []
latitudes = []  #
longitudes = []  #
hours_of_operations = []  ###

hours_key_list = [
    ["MonOpen", "MonClose"],
    ["TueOpen", "TueClose"],
    ["WedOpen", "WedClose"],
    ["ThuOpen", "ThuClose"],
    ["FriOpen", "FriClose"],
    ["SatOpen", "SatClose"],
    ["SunOpen", "SunClose"],
]


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


driver = get_driver("https://www.schuh.co.uk/stores/", "secondLine")

for search_lat, search_lon in search:
    while True:
        try:
            data = driver.execute_async_script(
                r"""
                var done = arguments[0]
                fetch('https://schuhservice.schuh.co.uk/StoreFinderService/GetNearbyBranchesByLocation', {
            "headers": {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/json;charset=UTF-8;",
                "sec-ch-ua-mobile": "?0",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site"
            },
            "referrer": "https://www.schuh.co.uk/",
            "referrerPolicy": "strict-origin-when-cross-origin",
            "body": '{"lat":"""
                + str(search_lat)
                + r""","lon":"""
                + str(search_lon)
                + r""","culture":"en-gb"}',
            "method": "POST",
            "mode": "cors",
            "credentials": "include"
                })
                .then(res => res.json())
                .then(data => done(data))
                """
            )
            break
        except Exception:
            driver = get_driver(
                "https://www.schuh.co.uk/stores/", "secondLine", driver=driver
            )
            continue

    data = data["d"]
    data = (
        data.replace('"', "'")
        .replace("true", "True")
        .replace("false", "False")
        .replace("'s", "s")
    )

    try:
        data = ast.literal_eval(data)
    except Exception:
        continue

    for location in data:
        locator_domain = "schuh.co.uk"
        page_url = "https://www.schuh.co.uk/stores/" + location[
            "BranchName"
        ].lower().replace(" ", "-")
        location_name = location["BranchName"]
        city = location["BranchCity"]
        zipp = location["BranchPostcode"]
        country_code = "UK"
        store_number = location["BranchRef"]
        phone = location["BranchPhone"]
        latitude = location["BranchLatitude"]
        longitude = location["BranchLongitude"]

        while True:
            try:
                location_data = driver.execute_async_script(
                    r"""
                    var done = arguments[0]
                    fetch("https://schuhservice.schuh.co.uk/StoreFinderService/GetAdditionalBranchInfo", {
                    "headers": {
                        "accept": "application/json, text/javascript, */*; q=0.01",
                        "accept-language": "en-US,en;q=0.9",
                        "cache-control": "no-cache",
                        "content-type": "application/json;charset=UTF-8;",
                        "sec-ch-ua-mobile": "?0",
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-site"
                    },
                    "referrer": "https://www.schuh.co.uk/",
                    "referrerPolicy": "strict-origin-when-cross-origin",
                    "body": '{"branchName":\""""
                    + location["BranchName"].lower().replace(" ", "-")
                    + r"""\","culture":"en-gb"}',
                    "method": "POST",
                    "mode": "cors",
                    "credentials": "include"
                    })
                    .then(res => res.json())
                    .then(data => done(data))
                    """
                )
                break
            except Exception:
                driver = get_driver(
                    "https://www.schuh.co.uk/stores/", "secondLine", driver=driver
                )
                continue

        location_data = location_data["d"]

        location_data = (
            location_data.replace('"', "'")
            .replace("true", "True")
            .replace("false", "False")
            .replace("\\", "")
            .split(",'BranchLocalInfo'")[0]
            .replace("'s", "s")
            + "}"
        )

        location_data = ast.literal_eval(location_data)

        address = (
            location_data["BranchAddress1"] + " " + location_data["BranchAddress2"]
        )

        hours = ""
        for open_key, close_key in hours_key_list:
            day = open_key[:3]
            open = str(location_data[open_key])
            end = str(location_data[close_key])

            hours = hours + day + " " + open + "-" + end + ", "
        hours = hours[:-2]

        state = "<MISSING>"
        location_type = "<MISSING>"

        search.found_location_at(latitude, longitude)

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

driver.quit()
