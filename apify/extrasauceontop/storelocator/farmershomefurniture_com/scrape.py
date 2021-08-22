from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from bs4 import BeautifulSoup as bs
import cloudscraper

search = DynamicZipSearch(country_codes=[SearchableCountries.USA])

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
scraper = cloudscraper.create_scraper(sess=session)

for search_code in search:
    url = "https://secure.gotwww.com/gotlocations.com/microd/farmershomefurniture.com/index.php"
    params = {
        "brand": "",
        "MinZoom": "",
        "MaxDistance": "",
        "address": search_code,
        "bypass": "y",
        "Submit": "search",
        "language": "",
    }

    response = session.post(url, data=params).text
    lines = response.split("\n")

    good_lines = [line for line in lines if "L.marker" in line]

    for location in good_lines:
        locator_domain = "https://www.farmershomefurniture.com/"
        page_url = location.split('href="')[1].split('"')[0]
        location_name = location.split('target="new">')[1].split("<")[0]
        if location_name == "name":
            continue
        address = location.split("class=address>")[1].split("<")[0]
        city = location.split("class=city>")[1].split("<")[0].strip().replace(",", "")
        state = location.split("state>")[1].split(" <")[0]
        zipp = location.split("class=zip>")[1].split("<")[0]
        country_code = "US"
        try:
            store_number = location.split("mailto:Store")[1].split("@")[0]
        except Exception:
            store_number = "<MISSING>"
        phone = location.split('<a href="tel:')[1].split('"')[0]
        location_type = "<MISSING>"
        latitude = location.split("marker([")[1].split(",")[0]
        longitude = location.split(",")[1].split("]")[0]
        try:
            hours = location.split("hours: ")[1].split("<")[0]
        except Exception:
            try:
                hours_data = scraper.get(page_url).text
                hours_soup = bs(hours_data, "html.parser")
                hours = (
                    hours_soup.find("div", attrs={"class": "grid-30"})
                    .text.strip()
                    .split("Store Hours")[1]
                    .split("Email")[0]
                    .replace("\n", " ")
                )
            except Exception:
                hours = "<MISSING>"
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
