from bs4 import BeautifulSoup as bs
import pandas as pd
from sgrequests import SgRequests
import json

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
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

url = "https://www.potatocornerusa.com"
response = session.get(url, headers=headers).text
soup = bs(response, "html.parser")

script = soup.find("script", attrs={"id": "wix-viewer-model"}).text.strip()
data = json.loads(script)

for key in data["siteFeaturesConfigs"]["router"]["routes"]:
    route = key[1:]
    location_url = url + route
    location_data = session.get(location_url).text
    if "Store Address" in location_data and route != "/store-template":

        soup = bs(location_data, "html.parser")
        locator_domain = "potatocornerusa.com"
        page_url = location_url
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours = "<MISSING>"

        location_name = soup.find("span", attrs={"class": "color_28"}).text.strip()
        full_address_and_phone = soup.find_all(
            attrs={"style": "font-family:montserrat,sans-serif"}
        )

        for item in full_address_and_phone:
            if item.text.strip() == "Store Address:":
                full_address = (
                    full_address_and_phone[full_address_and_phone.index(item) + 1]
                    .text.strip()
                    .replace("\n", ",")
                    .replace("Adress: ", "")
                    .split(" ")
                )
                zipp = full_address[-1]
                if len(zipp) > 5:
                    zipp = zipp[1:]

                try:
                    int(zipp[-1])
                    state = full_address[-2].replace(",", "")
                    city = full_address[-3].replace(",", "")
                    city_parts = full_address[:-3]
                    street = ""
                    for part in city_parts:
                        street = street + part.replace(",", "") + " "

                except Exception:
                    zipp = "<MISSING>"
                    state = full_address[-1].replace(",", "")
                    city = full_address[-2].replace(",", "")
                    city_parts = full_address[:-2]
                    street = ""
                    for part in city_parts:
                        street = street + part.replace(",", "") + " "

            if item.text.strip() == "Phone Number:":
                phone = (
                    full_address_and_phone[full_address_and_phone.index(item) + 1]
                    .text.strip()
                    .replace("(", "")
                    .replace(") ", "-")
                )
                if "N/A" in phone:
                    phone = "<MISSING>"

        street = street.replace("Address:", "")
        locator_domains.append(locator_domain)
        page_urls.append(page_url)
        location_names.append(location_name)
        street_addresses.append(street)
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

df.to_csv("data.csv", index=False)
