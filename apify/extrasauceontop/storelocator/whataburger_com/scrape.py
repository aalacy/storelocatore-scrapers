from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
import pandas as pd

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
state_url = "https://locations.whataburger.com/directory.html"

response = session.get(state_url).text

soup = bs(response, "html.parser")
state_links = soup.find_all("a", attrs={"class": "Directory-listLink"})

location_urls = []
for a_tag in state_links:
    loc_count = (
        a_tag.find("span", attrs={"class": "Directory-listLinkText"})["data-count"]
        .replace("(", "")
        .replace(")", "")
    )

    if loc_count == "1":
        location_urls.append("https://locations.whataburger.com/" + a_tag["href"])

    else:
        state_url = "https://locations.whataburger.com/" + a_tag["href"]
        response = session.get(state_url).text

        state_soup = bs(response, "html.parser")
        city_links = state_soup.find_all("a", attrs={"class": "Directory-listLink"})

        for city_link in city_links:

            loc_count = (
                city_link.find("span", attrs={"class": "Directory-listLinkText"})[
                    "data-count"
                ]
                .replace("(", "")
                .replace(")", "")
            )

            if loc_count == "1":
                location_urls.append(
                    "https://locations.whataburger.com/" + city_link["href"]
                )

            else:
                city_url = "https://locations.whataburger.com/" + city_link["href"]
                response = session.get(city_url).text

                location_soup = bs(response, "html.parser")
                single_location_links = location_soup.find_all(
                    "a", attrs={"class": "Teaser-titleLink"}
                )
                for single_location_link in single_location_links:
                    location_urls.append(
                        "https://locations.whataburger.com/"
                        + single_location_link["href"]
                    )

for location_url in location_urls:
    response = session.get(location_url).text
    soup = bs(response, "html.parser")

    locator_domain = "whataburger.com"
    page_url = location_url.replace("../", "")
    location_name = soup.find(
        "span", attrs={"itemprop": "name", "id": "location-name"}
    ).text
    address = soup.find("span", attrs={"class": "c-address-street-1"}).text
    city = soup.find("span", attrs={"class": "c-address-city"}).text
    state = page_url.split("/")[-3].upper()
    if len(state) > 3:
        state = page_url.split("/")[-4]
    zipp = soup.find("span", attrs={"class": "c-address-postal-code"}).text
    country_code = "US"
    store_number = location_name.split(" ")[-1].replace("#", "")
    phone = soup.find("div", attrs={"id": "phone-main"}).text
    location_type = "<MISSING>"
    latitude = soup.find("meta", attrs={"itemprop": "latitude"})["content"]
    longitude = soup.find("meta", attrs={"itemprop": "longitude"})["content"]

    hour_sections = soup.find("div", attrs={"class": "HoursToday-dineIn"}).find("span")[
        "data-days"
    ]
    hour_sections = json.loads(hour_sections)

    hours = ""
    for section in hour_sections:
        try:
            day = section["day"]
            start = section["intervals"][0]["start"]
            end = section["intervals"][0]["end"]
            hours = hours + day + " " + str(start) + "-" + str(end) + ", "
        except Exception:
            day = section["day"]
            hours = hours + day + " closed" + ", "

    hours = hours[:-2]

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
