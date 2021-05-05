from sgselenium import SgChrome
import json
import pandas as pd

type_dict = {
    "1": "hospital",
    "3": "emergency room",
    "2": "clinic and outpatient center",
    "5": "urgent care",
    "6": "walk in care",
    "7": "pharmacy",
    "4": "imaging",
}

start_url = "https://www.novanthealth.org/"
while True:
    try:
        with SgChrome() as driver:
            driver.get(start_url)
            data = driver.execute_async_script(
                f"""
            var done = arguments[0]
            fetch('https://www.novanthealth.org/DesktopModules/NHLocationFinder/API/Location/ByType', {{
                "headers": {{
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "x-requested-with": "XMLHttpRequest"
                }},
                "body": "LocationGroupId=1&Latitude=&Longitude=&Distance=5&SubTypes=&Keyword=&SortOrder=&MaxLocations=5000&MapBounds=",
                "method": "POST"
            }})
            .then(res => res.json())
            .then(data => done(data))
            """
            )
        break
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
for location in data["Locations"]:
    locator_domain = "novanthealth.org"
    page_url = location["WebsiteUrl"]
    location_name = location["BusinessName"]
    address = location["AddressLine"]
    city = location["City"]
    state = location["State"]
    zipp = location["PostalCode"]
    country_code = "US"
    store_number = location["StoreCode"].replace("-", "")
    phone = location["PrimaryPhone"]
    try:
        location_type_keys = location["LocationTypeIds"]
        location_type = "<MISSING>"
        for item in location_type_keys:
            if str(item) in type_dict.keys():
                location_type = type_dict[str(item)]
                break
    except Exception:
        location_type = "<MISSING>"
    latitude = location["Latitude"]
    longitude = location["Longitude"]
    hours = ""
    if "Open 24 hours" in location["HoursInfo"]["Display"].keys():
        hours = "Open 24 hours"
    else:
        days = location["HoursInfo"]["Display"].keys()
        for day in days:
            time = location["HoursInfo"]["Display"][day]
            hours = hours + day + " " + time + ", "
        hours = hours[:-2]
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
df.to_csv("data.csv", index=False)
