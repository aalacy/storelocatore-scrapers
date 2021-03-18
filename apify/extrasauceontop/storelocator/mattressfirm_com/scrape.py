from sgrequests import SgRequests
import json
import pandas as pd
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from bs4 import BeautifulSoup as bs


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                except Exception:
                    pass
        count = count + 1

    return json_objects


session = SgRequests()

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA], max_search_results=20
)

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
    "User-Agent": "PostmanRuntime/7.19.0",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
}

session = SgRequests(retry_behavior=None)


def getdata():
    for zipcode in search:
        search_url = (
            "https://maps.mattressfirm.com/api/getAsyncLocations?template=search&level=search&radius=100&search="
            + zipcode
        )
        response = session.get(search_url, headers=headers).json()

        coords = []

        if response["markers"] is None:
            search.mark_found(coords)
            continue
        for location in response["markers"]:

            soup = bs(location["info"], "html.parser")

            locator_domain = "mattressfirm.com"
            page_url = search_url
            location_name = soup.find("div", attrs={"class": "store-name"}).text.strip()
            address = soup.find(
                "span", attrs={"class": "block address-1 bold fc-gray"}
            ).text.strip()
            city = (
                soup.find("span", attrs={"class": "block address-zip bold fc-gray"})
                .text.strip()
                .split(",")[0]
                .strip()
            )
            state = (
                soup.find("span", attrs={"class": "block address-zip bold fc-gray"})
                .text.strip()
                .split(",")[1]
                .strip()
            )
            zipp = (
                soup.find("span", attrs={"class": "block address-zip bold fc-gray"})
                .text.strip()
                .split(",")[2]
                .strip()
            )
            country_code = "US"

            phone = soup.find("a", attrs={"class": "phone"}).text.strip()
            location_type = (
                soup.find("div", attrs={"class": "popup map-list-item-wrap"})[
                    "data-particles"
                ]
                .replace("Is", "")
                .strip()
            )

            latitude = location["lat"]
            longitude = location["lng"]

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
            coords.append([latitude, longitude])

        json_objects = extract_json(response["maplist"])
        for y in range(len(json_objects)):

            if y % 3 == 0:
                store_number = json_objects[y]["store-id"]
                store_numbers.append(store_number)

            elif y % 3 == 2:
                try:
                    day_hours = json_objects[y]["days"]
                    days = day_hours.keys()
                    hours = ""
                    for day in days:
                        hours = (
                            hours
                            + day
                            + " "
                            + day_hours[day][0]["open"]
                            + "-"
                            + day_hours[day][0]["close"]
                            + ", "
                        )

                    hours = hours[:-2]
                    hours_of_operations.append(hours)

                except Exception:
                    hours = "<MISSING>"
                    hours_of_operations.append(hours)

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
            "country_code": country_codes,
            "location_type": location_types,
            "hours_of_operation": hours_of_operations,
        }
    )

    return df


df = getdata()

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
