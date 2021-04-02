from sgrequests import SgRequests
import json
import pandas as pd
from sgzip.dynamic import DynamicZipSearch, SearchableCountries

session = SgRequests()
headers = {"accept": "application/json"}
search = DynamicZipSearch(country_codes=[SearchableCountries.USA], max_radius_miles=10)

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

for search_code in search:
    response = session.get(
        "https://locations.whataburger.com/search.html?q="
        + search_code
        + "&qp="
        + search_code
        + "&l=en",
        headers=headers,
    ).text
    response = json.loads(response)
    locations = response["response"]["entities"]
    with open("file.txt", "w", encoding="utf-8") as output:
        json.dump(locations, output, indent=4)

    for location in locations:
        locator_domain = "whataburger.com"
        page_url = location["profile"]["c_pagesWebsiteURL"]
        try:
            location_name = location["profile"]["c_locationNickname"]
        except Exception:
            location_name = location["profile"]["c_locationName"]
        address = location["profile"]["address"]["line1"]
        city = location["profile"]["address"]["city"]
        state = location["profile"]["address"]["region"]
        zipp = location["profile"]["address"]["postalCode"]
        country_code = location["profile"]["address"]["countryCode"]
        store_number = location["distance"]["id"]
        phone = location["profile"]["mainPhone"]["number"].replace("+", "")
        location_type = location["profile"]["c_locationType2"]

        try:
            latitude = location["profile"]["geocodedCoordinate"]["lat"]
            longitude = location["profile"]["geocodedCoordinate"]["long"]
            search.found_location_at(latitude, longitude)
        except Exception:
            try:
                latitude = location["profile"]["displayCoordinate"]["lat"]
                longitude = location["profile"]["displayCoordinate"]["long"]
                search.found_location_at(latitude, longitude)
            except Exception:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

        hours = ""
        try:
            for item in location["profile"]["c_dineInHours"]["normalHours"]:
                day = item["day"]
                start_time = str(item["intervals"][0]["start"])
                if start_time == 0 or start_time == "0":
                    start_time = "000"
                start_time = start_time[:-2] + ":" + start_time[-2:]
                end_time = str(item["intervals"][0]["end"])
                if end_time == 0 or end_time == "0":
                    end_time = "000"
                end_time = end_time[:-2] + ":" + end_time[-2:]

                hours = hours + day + " " + start_time + "-" + end_time + ", "

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
        phones.append(phone)
        location_types.append(location_type)
        latitudes.append(latitude)
        longitudes.append(longitude)
        store_numbers.append(store_number)
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
        "country_code": country_codes,
        "location_type": location_types,
        "hours_of_operation": hours_of_operations,
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
