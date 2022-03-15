from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])

session = SgRequests()

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

week_days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

for search_lat, search_lon in search:

    url = (
        "https://www.cheddars.com/web-api/restaurants?geoCode="
        + str(search_lat)
        + "%2C"
        + str(search_lon)
        + "&resultsPerPage=500&resultsOffset=0&pdEnabled=&reservationEnabled=&isToGo=&privateDiningEnabled=&isNew=&displayDistance=true&locale=en_US"
    )
    response = session.post(url).json()

    try:
        locations = response["successResponse"]["locationSearchResult"]["Location"]
    except Exception:
        continue
    for location in locations:
        locator_domain = "cheddars.com"
        page_url = url
        location_name = location["restaurantName"]
        address = location["AddressOne"]
        city = location["city"]
        state = location["state"]
        zipp = location["zip"]
        if len(zipp) == 9:
            zipp = str(zipp[:5]) + "-" + str(zipp[5:])
        country_code = location["country"]
        store_number = location["restaurantNumber"]
        phone = location["phoneNumber"]
        location_type = "<MISSING>"
        latitude = location["latitude"]
        longitude = location["longitude"]

        hours = ""
        for item in location["weeklyHours"]:
            if item["hourTypeDesc"] == "Hours of Operations":
                index = item["dayOfWeek"]
                day = week_days[index - 1]

                start_time = item["startTime"]
                end_time = item["endTime"]

                hours = hours + day + " " + start_time + "-" + end_time + ", "

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

        search.found_location_at(latitude, longitude)

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
