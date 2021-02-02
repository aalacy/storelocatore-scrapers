from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re


def getdata():
    session = SgRequests()
    response = session.get(
        "https://www.google.com/maps/d/kml?mid=1k_5K2ikpmcAyElx_ND0io5MT-3w&forcekml=1"
    ).text

    soup = bs(response, "html.parser")

    places = soup.find_all("placemark")

    latitudes = []
    longitudes = []

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

    for place in places:
        name = place.find("name").text.strip()
        street = place.find(attrs={"name": "Address"}).text.strip()
        city = place.find(attrs={"name": "City"}).text.strip()
        state = place.find(attrs={"name": "State"}).text.strip()
        zip_code = place.find(attrs={"name": "ZIP"}).text.strip()
        phone = place.find(attrs={"name": "Phone"}).text.strip()
        hour = place.find(attrs={"name": "Store Hrs."}).text.strip()
        page_url = "https://www.google.com/maps/d/viewer?mid=1k_5K2ikpmcAyElx_ND0io5MT-3w&ll=35.64271937457243%2C-88.47843979999999&z=4"

        # for some reason the 0 is trimmed off of zip codes beginning with 0. Add that back here
        if len(zip_code) == 4:
            zip_code = "0" + zip_code
        names.append(name)
        addresses.append(street)
        citys.append(city)
        states.append(state)
        zips.append(zip_code)
        phones.append(phone)
        hours.append(hour)
        page_urls.append(page_url)

        locator_domains.append("premierrents.net")
        country_codes.append("US")
        location_types.append("<MISSING>")
        store_numbers.append("<MISSING>")

    # This section calls to the map page to extract the latitudes and longitudes view regex
    response = session.get(
        "https://www.google.com/maps/d/viewer?mid=1k_5K2ikpmcAyElx_ND0io5MT-3w&ll=35.64271937457243%2C-88.47843979999999&z=4"
    ).text
    result = re.search(r"_pageData = (.*)script", response)
    result = result.group(1)
    result = result.split("\\n")

    for line in result:
        coords = re.search(r"\",\[\[\[(.*)\]", line)
        if coords:
            coords = coords.group(1)
            coords = coords.split(",")
            if len(coords) == 2:
                latitudes.append(coords[0])
                longitudes.append(coords[1])

    df = pd.DataFrame(
        {
            "locator_domain": locator_domains,
            "page_url": page_urls,
            "location_name": names,
            "latitude": latitudes,
            "longitude": longitudes,
            "street_address": addresses,
            "city": citys,
            "state": states,
            "zip": zips,
            "phone": phones,
            "hours_of_operation": hours,
            "country_code": country_codes,
            "location_type": location_types,
            "store_number": store_numbers,
        }
    )

    writedata(df)


def writedata(df):
    df = df.replace(r"^\s*$", "<MISSING>", regex=True)
    df.to_csv("data.csv", index=False)


getdata()
