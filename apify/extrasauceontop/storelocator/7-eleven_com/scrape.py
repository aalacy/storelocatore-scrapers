from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])

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
    "Authority": "www.7-eleven.com",
    "Method": "GET",
    "Path": "/locator",
    "Scheme": "https",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36",
}

response = session.get("https://www.7-eleven.com/locator", headers=headers).text
auth_token = response.split('access_token":')[1].split('"')[1]


headers = {
    "Authorization": "Bearer " + auth_token,
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36",
    "Host": "api.7-eleven.com",
    "Origin": "https://www.7-eleven.com",
    "Referer": "https://www.7-eleven.com/",
    "Accept": "application/json, text/plain, */*",
}

for search_lat, search_lon in search:
    coords = []
    url = f"https://api.7-eleven.com/v4/stores?lat={search_lat}&lon={search_lon}&radius=10000&curr_lat={search_lat}&curr_lon={search_lon}&limit=500&features="

    data = session.get(url, headers=headers).json()

    locations = data["results"]

    for location in locations:
        locator_domain = "7-eleven.com"
        page_url = url
        location_name = location["name"]
        address = location["address"]
        city = location["city"]
        state = location["state"]
        country_code = location["country"]
        zipp = location["zip"]

        if zipp[0] == 0:
            zipp = "0" + str(zipp)
        elif len(str(zipp)) == 4:
            zipp = "0" + str(zipp)
        store_number = location["id"]
        phone = location["phone"]
        if len(phone) < 5:
            phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = location["lat"]
        longitude = location["lon"]

        hours = ""
        if location["open_time"] == "24h":
            hours = location["open_time"]
        else:
            try:
                for item in location["hours"]["operating"]:
                    hours = hours + item["key"] + " "
                    hours = hours + item["detail"] + ", "

                hours = hours[:-2]
            except Exception:
                hours = "<MISSING>"

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

df.to_csv("data.csv", index=False)
