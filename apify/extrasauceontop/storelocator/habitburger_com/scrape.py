from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd


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
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
}

url = "https://www.habitburger.com/locations/all/"
all_stores = session.get(url).text

soup = bs(all_stores, "html.parser")
all_pages = soup.find_all("div", attrs={"class": "locbtn"})

page_urls_to_iterate = [
    "https://www.habitburger.com" + location.find("a")["href"]
    for location in all_pages
    if location.find("a")["href"][0] == "/"
]

for url in page_urls_to_iterate:
    locator_domain = "habitburger.com"

    response = session.get(url).text.replace(
        "https://habitburger.fbmta.com/shared/images/275/275_2021012818164353.jpg", ""
    )

    json_objects = extract_json(response)
    location = json_objects[-1]

    location_name = location["address"]["addressLocality"]
    city = location_name
    state = location["address"]["addressRegion"]
    country_code = location["address"]["addressCountry"]
    zipp = location["address"]["postalCode"]

    if zipp == "":
        continue

    address = (
        location["address"]["streetAddress"]
        .replace(city + " " + state + " " + zipp, "")
        .strip()
    )

    if "blvdTerminal" in address:
        address = address.replace("blvdTerminal", "blvd Terminal")
    store_number = "<MISSING>"

    try:
        phone = location["telephone"]
    except Exception:
        "<MISSING>"
    location_type = location["@type"]

    lat_lon_text = extract_json(
        response.split("google.maps.Marker({")[1]
        .replace("lat", '"lat"')
        .replace("lng", '"lng"')
    )[0]
    latitude = lat_lon_text["lat"]
    longitude = lat_lon_text["lng"]

    hours = location["openingHours"][0]
    if hours == "":
        check = response.split("Hours")[1].split("div")[0]

        if "Temporarily Closed" in response:
            hours = "Temporarily Closed"

        elif "Coming Soon" in response:
            hours = "Opening Soon"

        elif "Dining Room & Drive-Thru" in response:
            check = check.split("<br>")
            check = check[:-1]
            x = 0
            for section in check:
                if x == 0:
                    x = 1
                    continue
                hours = hours + section + ", "

        elif "Dining Room" in check:
            check = check.split("<br>")
            check = check[:-1]
            x = 0
            for section in check:
                if x == 0:
                    x = 1
                    continue
                if "h2" in section:
                    break
                hours = hours + section + ", "

        elif len(check.split("\n")) == 2:
            check = check.split("\n")[1].split("<br>")

            for item in check:
                hours = hours + item.rstrip() + " "

            hours = hours.replace("</", "").strip()
            hours = hours.strip()

        elif location_name == "Reno":
            check = check.split("\n")[1:]
            for item in check:
                item = item.replace("\r", "")
                item = (
                    item.replace('<h2 class="hdr">', "")
                    .replace('</h2 class="hdr"><br>', "")
                    .replace("<br>", "")
                    .replace("                        </", "")
                )
                hours = hours + item + " "

            hours = hours.strip()

        elif location_name == "Phoenix":
            hours = check.split("\n")[1].replace("<br>", "").strip()

        else:
            hours = "<MISSING>"

    locator_domains.append(locator_domain)
    page_urls.append(url)
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
