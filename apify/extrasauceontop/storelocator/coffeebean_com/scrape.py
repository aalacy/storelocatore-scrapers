from sgrequests import SgRequests
import pandas as pd
from bs4 import BeautifulSoup as bs
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
import us
import re

locator_domains = []
websites = []
locations = []
names = []
addresses = []
citys = []
states = []
zips = []
countrys = []
stores = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_op = []

session = SgRequests()
search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])

base_url = "https://www.coffeebean.com/store-locator"

# Country search
locs = []
for x in range(101):
    params = {"field_country_value": "USA", "page": x}
    r = session.get(base_url, params=params).text
    soup = bs(r, "html.parser")
    view_store = soup.find_all("a", attrs={"class": "view-store"})
    for item in view_store:
        locs.append(item["href"])

# Lat Lng Boundary search
base_url = "https://www.coffeebean.com/store-locator?field_geo_location_boundary%5Blat_north_east%5D=47.56&field_geo_location_boundary%5Blng_north_east%5D=69.44&field_geo_location_boundary%5Blat_south_west%5D=16.11&field_geo_location_boundary%5Blng_south_west%5D=-178.85"
for x in range(101):
    params = {"page": x}

    r = session.get(base_url, params=params).text

    soup = bs(r, "html.parser")
    view_store = soup.find_all("a", attrs={"class": "view-store"})
    for item in view_store:
        locs.append(item["href"])

# All search
for x in range(101):
    url = "https://www.coffeebean.com/store-locator?&page=" + str(x)
    r = session.get(url).text
    soup = bs(r, "html.parser")
    view_store = soup.find_all("a", attrs={"class": "view-store"})
    for item in view_store:
        locs.append(item["href"])

locs_df = pd.DataFrame({"locs": locs})
locs_df = locs_df.drop_duplicates()
locs = locs_df["locs"].to_list()

for loc in locs:
    r = session.get(loc)
    name = ""
    add = ""
    city = ""
    state = ""
    zc = ""
    typ = "<MISSING>"
    country = ""
    store = "<MISSING>"
    phone = "<MISSING>"
    lat = ""
    lng = ""
    hours = ""
    website = loc
    for line in r.iter_lines(decode_unicode=True):
        if '<span class="field-content">' in line:
            name = line.split('<span class="field-content">')[1].split("<")[0]
        if '<span property="streetAddress">' in line:
            add = line.split('<span property="streetAddress">')[1].split("<")[0]
        if '<span property="addressLocality">' in line:
            city = line.split('<span property="addressLocality">')[1].split("<")[0]
        if '<span property="addressRegion">' in line:
            state = line.split('<span property="addressRegion">')[1].split("<")[0]
        if '<span property="addressCountry">' in line:
            country = line.split('<span property="addressCountry">')[1].split("<")[0]
            # remove non-alpha characters
            country = re.sub(r"[^a-zA-Z\s]", "", country)
            if country == "United States":
                country = "USA"
        if '<span property="telephone">' in line:
            phone = line.split('<span property="telephone">')[1].split("<")[0]
        if '<span property="postalCode">' in line:
            zc = line.split('<span property="postalCode">')[1].split("<")[0]
        if '<meta property="latitude" content="' in line:
            lat = line.split('<meta property="latitude" content="')[1].split('"')[0]
        if '<meta property="longitude" content="' in line:
            lng = line.split('<meta property="longitude" content="')[1].split('"')[0]
        if "name-field-weekday" in line:
            day = line.split('">')[1].split("<")[0]
        if "name-field-store-open" in line:
            hro = line.split('">')[1].split("<")[0]
        if "name-field-store-closed" in line:
            hrs = day + ": " + hro + "-" + line.split('">')[1].split("<")[0]
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
    if hours == "":
        hours = "<MISSING>"
    if lat == "":
        lat = "<MISSING>"
        lng = "<MISSING>"
    if name == "":
        name = city
    if phone == "NULL":
        phone = "<MISSING>"
    if add == "":
        add = "<MISSING>"
    if zc == "":
        zc = "<MISSING>"
    if country in ["", "NULL"]:
        if us.states.lookup(state):
            country = "USA"

    x = x + 1
    if country == "USA":
        locator_domains.append("coffeebean.com")
        websites.append(website)
        locations.append(loc)
        names.append(name)
        addresses.append(add)
        citys.append(city)
        states.append(state)
        zips.append(zc)
        countrys.append(country)
        stores.append(store)
        phones.append(phone)
        location_types.append(typ)
        latitudes.append(lat)
        longitudes.append(lng)
        hours_op.append(hours)

df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": websites,
        "location_name": names,
        "street_address": addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": stores,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_op,
        "country_code": countrys,
        "location_type": typ,
    }
)

data = df.drop_duplicates()
data.to_csv("data.csv", index=False)
