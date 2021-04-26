from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(country_codes=[SearchableCountries.CANADA])

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

url = "https://chatime.com/wp-admin/admin-ajax.php"
headers = {
    "referer": "https://chatime.com",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
}
days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

for search_lat, search_lon in search:
    coords = []
    params = {
        "action": "get_stores",
        "lat": search_lat,
        "lng": search_lon,
        "radius": "999",
    }
    response = session.post(url, headers=headers, data=params).json()

    for key in response:
        location = response[key]

        locator_domain = "chatime.com"
        page_url = location["gu"]
        location_name = location["na"]
        address = location["st"]
        city = location["ct"]
        state = location["rg"]
        zipp = location["zp"]
        country_code = location["co"]
        store_number = location["ID"]
        try:
            phone = location["te"]
        except Exception:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = location["lat"]
        longitude = location["lng"]

        hour_part = location["op"]
        hours = ""
        for x in range(14):
            if x % 2 == 0:
                day = days[int(x / 2)]
                opening = hour_part[str(x)].strip()
                closing = hour_part[str(x + 1)].strip()

                hours = hours + day + " " + opening + "-" + closing + ", "

        hours = hours.strip()[:-1]

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

        current_coords = [latitude, longitude]
        coords.append(current_coords)
    search.mark_found(coords)

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

df.to_csv("data.csv", index=True)
