from sgrequests import SgRequests
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


session = SgRequests()
url = "https://services.publix.com/api/v1/storelocation?types=W&count=15&distance=32767&includeStore=true&includeOpenAndCloseDates=true&storeNumber=1573"
response = session.get(url).json()

for location in response["Stores"]:
    locator_domain = "greenwisemarket.com"
    page_url = url
    location_name = location["NAME"]
    address = location["ADDR"]
    city = location["CITY"]
    state = location["STATE"]
    zipp = location["ZIP"]
    country_code = "US"
    store_number = location["KEY"]
    phone = location["PHONE"]
    location_type = "<MISSING>"
    latitude = location["CLAT"]
    longitude = location["CLON"]
    hours = location["STRHOURS"]

    if location["STATUS"] == "Coming Soon":
        hours = "Coming Soon"

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
