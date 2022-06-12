from sgrequests import SgRequests
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

session = SgRequests()

headers = {
    "User-Agent": "PostmanRuntime/7.19.0",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}

response = session.get(
    "https://www.haineandsmith.co.uk/views/display_stores.php", headers=headers
).json()
response = response["locations"]

for location in response:
    locator_domain = "haineandsmith.co.uk/"
    page_url = locator_domain + location["url"]
    location_name = location["name"]

    full_address = location["address"]
    full_address_split = full_address.replace(",", "").replace("  ", " ").split(" ")

    zipp = full_address_split[-2] + full_address_split[-1]
    state = full_address_split[-3]
    city = full_address_split[-4]
    street_address = full_address_split[: len(full_address_split) - 4]

    address = ""
    for item in street_address:
        address = address + item + " "
    address = address.strip()

    country_code = "UK"
    store_number = location["id"]
    phone = location["tel"]

    location_type = "<MISSING>"

    longitude = location["lng"]
    latitude = location["lat"]

    hours = ""

    hour_soup = (
        bs(session.get("https://" + page_url, headers=headers).text, "html.parser")
        .find("table", attrs={"class": "fleft small"})
        .text.split("\n")
    )
    for item in hour_soup:
        if item == "":
            pass
        else:
            hours = hours + item + " "

    hours = hours.strip()

    if city == "Street":
        city = state
        state = "<MISSING>"

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

df.to_csv("data.csv", index=False)
