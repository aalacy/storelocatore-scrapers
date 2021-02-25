from sgrequests import SgRequests
import pandas as pd
from bs4 import BeautifulSoup as bs
import re

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

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

sitemap_url = "https://www.adidas.co.uk/glass/sitemaps/adidas/GB/en/sitemaps/store-pages-sitemap.xml"
session = SgRequests()

response = session.get(sitemap_url, headers=headers, timeout=10).text

soup = bs(response, "html.parser")
urls = soup.find_all("loc")

base_url = "https://www.adidas.co.uk/api/storefront/stores/"

for url in urls:

    url_text = url.text.strip()
    if url_text == "www.adidas.co.uk/storefront":
        pass
    else:
        api_code = url_text.split("storefront/")[1].split("-")[0]

        store_data = session.get(
            base_url + api_code, headers=headers, timeout=10
        ).json()

        city = store_data["city"]

        if city.lower() == "online":
            pass
        else:
            key_check = store_data.keys()
            if "phoneNumber" in key_check:
                phone = store_data["phoneNumber"].replace("+", "")
            else:
                phone = "<MISSING>"

            if "postcode" in key_check:
                zipp = store_data["postcode"]
            else:
                zipp = "<MISSING>"

            locator_domain = "adidas.co.uk"
            page_url = base_url + api_code
            location_name = store_data["name"]
            address = store_data["street"]
            state = "<MISSING>"
            country_code = store_data["country"]
            store_number = store_data["id"]

            location_type = "<MISSING>"
            latitude = store_data["coordinates"]["lat"]
            longitude = store_data["coordinates"]["lng"]

            hours = store_data["openingHours"]

            hours_op = ""
            for day in hours:
                keys = day.keys()

                for key in keys:
                    hours_op = hours_op + " " + day[key]

            if bool(re.search(r"\d", hours_op)) is False:
                hours_op = "<MISSING>"

            if int(latitude) == 0 and int(longitude) == 0:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

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
            hours_of_operations.append(hours_op)


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

df = df.drop_duplicates(subset=["location_name"])
df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df.to_csv("data.csv", index=False)
