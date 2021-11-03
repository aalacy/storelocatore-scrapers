from sgselenium import SgChrome
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from webdriver_manager.chrome import ChromeDriverManager

search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])

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

base_url = "https://online.citi.com/US/ag/citibank-location-finder"

driver = SgChrome(
    is_headless=True, executable_path=ChromeDriverManager().install()
).driver()
driver.get(base_url)
for search_lat, search_lon in search:
    x = 0
    while True:
        x = x + 1
        try:
            data = driver.execute_async_script(
                """
                var done = arguments[0]
                fetch("https://online.citi.com/gcgapi/prod/public/v1/geoLocations/places/retrieve", {
                "headers": {
                    "accept": "application/json",
                    "accept-language": "en-US",
                    "businesscode": "GCB",
                    "channelid": "INTERNET",
                    "client_id": "4a51fb19-a1a7-4247-bc7e-18aa56dd1c40",
                    "content-type": "application/json; charset=UTF-8",
                    "countrycode": "US",
                    "scope": "VISITOR",
                    "sec-ch-ua-mobile": "?0",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin"
                },
                "referrer": "https://online.citi.com/US/ag/citibank-location-finder",
                "referrerPolicy": "strict-origin-when-cross-origin",
                "body": '{"type":"branchesAndATMs","inputLocation":["""
                + str(search_lon)
                + """, """
                + str(search_lat)
                + """],"resultCount":"1000","distanceUnit":"MILE","findWithinRadius":"1000000"}',
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
            driver.quit()
            driver = SgChrome(
                is_headless=True, executable_path=ChromeDriverManager().install()
            ).driver()
            driver.get(base_url)
            if x == 10:
                break
            continue

    for location in data["features"]:
        locator_domain = "online.citi.com"
        page_url = "https://online.citi.com/US/ag/citibank-location-finder"
        location_name = location["properties"]["additionalProperties"]["StoreName"]
        if location_name == "":
            location_name = location["properties"]["name"]
        address = location["properties"]["addressLine1"]
        city = location["properties"]["city"]
        state = location["properties"]["state"]
        zipp = str(location["properties"]["postalCode"])
        if len(zipp) == 4:
            zipp = "0" + zipp
        country_code = location["properties"]["additionalProperties"]["iso3_alpha"]
        if country_code != "USA":
            continue
        store_number = location["id"]
        phone = location["properties"]["additionalProperties"]["contactDetails"][
            "branchPhone"
        ]
        location_type = location["properties"]["type"]
        if (
            location_type == "moneypassatm"
            or location["properties"]["additionalProperties"]["Affiliation"]
            == "AllPoint"
        ):
            continue

        if location_type == "branch":
            location_type = "branch and atm"

        latitude = location["geometry"]["coordinates"][1]
        longitude = location["geometry"]["coordinates"][0]
        search.found_location_at(latitude, longitude)

        hours = location["properties"]["additionalProperties"]["ExternalNotes"].split(
            "|"
        )[0]

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
