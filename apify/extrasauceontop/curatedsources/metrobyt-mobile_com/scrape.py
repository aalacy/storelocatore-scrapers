from sgrequests import SgRequests
import pandas as pd

session = SgRequests()

url = "https://www.metrobyt-mobile.com/api/v1/commerce/store-locator?store-type=AuthorizedDealer&min-latitude=12.7086&max-latitude=71.286&min-longitude=-52.298&max-longitude=-170.371337"

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "accept": "application/json, text/plain, */*",
}
response = session.get(url, headers=headers).json()

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

for location in response:
    locator_domain = "metrobyt-mobile.com"
    page_url = url
    location_name = location["name"]
    address = location["location"]["address"]["streetAddress"]
    city = location["location"]["address"]["addressLocality"]
    state = location["location"]["address"]["addressRegion"]
    zipp = location["location"]["address"]["postalCode"]
    country_code = "US"
    store_number = location["id"]
    phone = location["telephone"]
    location_type = location["type"]
    latitude = location["location"]["latitude"]
    longitude = location["location"]["longitude"]

    hours = ""

    for section in location["openingHours"]:
        days = section["days"]
        section_hours = section["time"]
        for day in days:
            hours = hours + day + " " + section_hours + ", "

    hours = hours[:-2]

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
