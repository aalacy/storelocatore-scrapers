from sgrequests import SgRequests
import pandas as pd
from bs4 import BeautifulSoup as bs
import re
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

page_urls = []
locator_domains = []
country_codes = []
location_types = []
names = []
addresses = []
citys = []
states = []
zips = []
phones = []
hours = []
store_numbers = []
lats = []
lngs = []

search = DynamicZipSearch(country_codes=[SearchableCountries.BRITAIN])

session = SgRequests()

for zip_code in search:
    url = (
        "https://www.salvationarmy.org.uk/map-page?near%5Bvalue%5D="
        + str(zip_code)
        + "&near%5Bdistance%5D%5Bfrom%5D=40.22"
    )
    response = session.get(url).text

    soup = bs(response, "html.parser")

    grids = soup.find_all("div", attrs={"class": "geolocation-location js-hide"})

    coords = []
    for grid in grids:
        locator_domain = "salvationarmy.org.uk"
        page_url = url
        country_code = "UK"

        name = grid.find("p", attrs={"class": "field-content title"}).text.strip()

        full_address = grid.find("p", attrs={"class": "address"}).text.strip()
        full_address = full_address.split("\n")
        full_address = [item.strip() for item in full_address]

        address = full_address[0]

        city_zipp = full_address[1].replace("  ", " ").replace(",", "").split(" ")

        city = ""
        zipp = ""

        for item in city_zipp:
            if re.search(r"\d", item) is None:
                city = city + " " + item
            else:
                zipp = zipp + " " + item

        zipp = zipp.strip()
        city = city.strip()

        current_lat = grid["data-lat"]
        current_lng = grid["data-lng"]

        state = "<MISSING>"

        phone_list = grid.find("a").text.strip()
        phone = ""
        for item in phone_list:
            if re.search(r"\d", item) is not None:
                phone = phone + item
            if len(phone) == 11:
                break

        if phone == "":
            phone = "<MISSING>"

        hour = "<MISSING>"

        store_number = grid["id"]

        locator_domains.append(locator_domain)
        page_urls.append(page_url)
        country_codes.append(country_code)
        hours.append(hour)
        store_numbers.append(store_number)

        names.append(name)
        addresses.append(address)
        citys.append(city)
        states.append(state)
        zips.append(zipp)
        phones.append(phone)
        lats.append(current_lat)
        lngs.append(current_lng)

        coords.append([current_lat, current_lng])

    grids = soup.find_all("div", attrs={"class": "e-grid-column"})
    for grid in grids:
        location_type = grid.find("p").text.strip()
        location_types.append(location_type)

    search.mark_found(coords)


df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": names,
        "latitude": lats,
        "longitude": lngs,
        "street_address": addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "phone": phones,
        "hours_of_operation": hours,
        "country_code": country_codes,
        "store_number": store_numbers,
        "location_type": location_types,
    }
)


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
