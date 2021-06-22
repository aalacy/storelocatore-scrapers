from sgselenium import SgChrome
from webdriver_manager.chrome import ChromeDriverManager
import html
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

base_url = "https://www.maccosmetics.com/international-store-locator"

driver = SgChrome(
    is_headless=True, executable_path=ChromeDriverManager().install()
).driver()
driver.get(base_url)

coordinates_list = [[51.3810641, -2.3590167]]


for search_latitude, search_longitude in coordinates_list:

    data = driver.execute_async_script(
        """
        console.log("started")
        var done = arguments[0]
        fetch("https://www.maccosmetics.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents", {
        "headers": {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest"
        },
        "referrer": "https://www.maccosmetics.com/international-store-locator",
        "referrerPolicy": "strict-origin-when-cross-origin",
        "body": "JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A3%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+DOORNAME%2C+EVENT_NAME%2C+SUB_HEADING%2C+EVENT_START_DATE%2C+EVENT_END_DATE%2C+EVENT_IMAGE%2C+EVENT_FEATURES%2C+EVENT_TIMES%2C+SERVICES%2C+STORE_HOURS%2C+ADDRESS%2C+ADDRESS2%2C+STATE_OR_PROVINCE%2C+CITY%2C+REGION%2C+COUNTRY%2C+ZIP_OR_POSTAL%2C+PHONE1%2C+PHONE2%2C+STORE_TYPE%2C+LONGITUDE%2C+LATITUDE%2C+COMMENTS%22%2C%22country%22%3A%22United+States%22%2C%22latitude%22%3A"""
        + str(search_latitude)
        + """%2C%22longitude%22%3A"""
        + str(search_longitude)
        + """%2C%22uom%22%3A%22mile%22%2C%22region_id%22%3A0%2C%22radius%22%3A100000%7D%5D%7D%5D",
        "method": "POST",
        "mode": "cors",
        "credentials": "include"
        })
        .then(res => res.json())
        .then(data => done(data))
        """
    )

    locations = data[0]["result"]["value"]["doors"]
    for store_number in locations:
        location = data[0]["result"]["value"]["results"][str(store_number)]

        locator_domain = "maccosmetics.com"
        page_url = "<MISSING>"
        location_name = (
            html.unescape(location["DOORNAME"]) + " " + location["SUB_HEADING"]
        )
        address = location["ADDRESS"]
        city = location["CITY"]
        state = location["STATE_OR_PROVINCE"]
        zipp = location["ZIP_OR_POSTAL"]
        country_code = location["COUNTRY"]
        phone = location["PHONE1"]
        location_type = location["STORE_TYPE"]
        latitude = location["LATITUDE"]
        longitude = location["LONGITUDE"]

        hours_sections = location["STORE_HOURS"]

        hours = ""

        for section in hours_sections:
            try:
                hours = hours + section["day"] + " " + section["hours"] + ", "

            except Exception:
                pass

        if len(hours) > 1:
            hours = hours[:-2]

        if (
            country_code != "United States"
            and country_code != "US"
            and country_code != "USA"
        ):
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
