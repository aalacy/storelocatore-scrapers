from sgrequests import SgRequests
import pandas as pd
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import re

search = DynamicZipSearch(country_codes=[SearchableCountries.CANADA])
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
url = "https://on-api.mycarecompass.lifelabs.com/api/LocationFinder/GetLocations/"
false = False

for search_code in search:
    try:
        params = {
            "address": search_code,
            "locationCoordinate": {"latitude": 0, "longitude": 0},
            "locationFinderSearchFilters": {
                "isOpenEarlySelected": false,
                "isOpenWeekendsSelected": false,
                "isOpenSundaysSelected": false,
                "isWheelchairAccessibleSelected": false,
                "isDoesECGSelected": false,
                "isDoes24HourHolterMonitoringSelected": false,
                "isDoesAmbulatoryBloodPressureMonitoringSelected": false,
                "isDoesServeAutismSelected": false,
                "isGetCheckedOnlineSelected": false,
                "isOpenSaturdaysSelected": false,
                "isCovid19TestingSiteSelected": false,
            },
        }
        response = session.post(url, json=params).json()

        for location in response["entity"]:
            locator_domain = "lifelabs.com"
            page_url = (
                "https://www.on.mycarecompass.lifelabs.com/appointmentbooking?siteId="
                + str(location["locationId"])
            )
            location_name = location["pscName"]
            address = location["locationAddress"]["street"]
            x = 0
            for character in address:
                if bool(re.search(r"\d", character)) is True:
                    break

                x = x + 1
            address = address[x:]
            city = location["locationAddress"]["city"]
            state = location["locationAddress"]["province"]
            zipp = location["locationAddress"]["postalCode"]
            country_code = "CA"
            store_number = location["locationId"]
            phone = location["phone"]
            location_type = "<MISSING>"
            latitude = location["locationCoordinate"]["latitude"]
            longitude = location["locationCoordinate"]["longitude"]
            search.found_location_at(latitude, longitude)

            hours = ""
            x = 0
            days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
            for part in location["hoursOfOperation"]:

                try:
                    day = days[x]
                    start = part["openTime"]
                    end = part["closeTime"]
                    hours = hours + day + " " + start + "-" + end + ", "

                except Exception:
                    day = days[x]
                    hours = hours + day + " " + "closed" + ", "
                x = x + 1

            hours = hours[:-2]

            if (
                hours
                == "mon closed, tue closed, wed closed, thu closed, fri closed, sat closed, sun closed"
            ):
                continue

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

    except Exception:
        continue

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
