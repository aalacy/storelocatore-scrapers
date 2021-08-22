from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
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
url = "https://vitalitybowls.com/all-locations/"

response = session.get(url).text
soup = bs(response, "html.parser")

loc_urls = [
    a_tag["href"] for a_tag in soup.find_all("a", attrs={"class": "locationurl"})
]

for page_url in loc_urls:

    response = session.get(page_url).text
    soup = bs(response, "html.parser")
    locator_domain = "vitalitybowls.com"
    location_name = soup.find("h2", attrs={"class": "et_pb_slide_title"}).text.strip()
    if "What Are Our Customers Saying?" in location_name:
        location_name = (
            soup.find("div", attrs={"class": "et_pb_row et_pb_row_0"})
            .text.strip()
            .split("\n")[0]
        )

    address_parts = [
        item
        for item in soup.find_all("div", attrs={"class": "et_pb_text_inner"})[1]
        .text.strip()
        .split("\n")[1:]
        if item != ""
    ]

    if len(address_parts) == 1:
        address = ""
        street_parts = address_parts[0].split(",")[0].split(" ")[:-1]

        for part in street_parts:
            address = address + part + " "

        address = address.strip()

        city = address_parts[0].split(",")[0].split(" ")[-1]

        state = address_parts[0].split(", ")[1].split(" ")[0]
        zipp = address_parts[0].split(", ")[1].split(" ")[1]

    elif len(address_parts) == 0:
        address_parts = (
            soup.text.split("STORE INFO")[1]
            .split("\n")[0]
            .strip()
            .split("Pleasant Hill")
        )

        address = address_parts[0]
        city = "Pleasant Hill"
        state = address_parts[1].split(" ")[1]
        zipp = address_parts[1].split(" ")[-1]

    else:
        address_index = -1
        for part in address_parts:
            if bool(re.search(r"\d", part[0])) is True:
                address = part
                address_index = address_parts.index(part)

                if len(address_parts) - address_index == 3:
                    address = address.strip() + " " + address_parts[address_index + 1]

        try:
            city = address_parts[-1].split(",")[0]
            state = address_parts[-1].split(", ")[1][0:2]
            zipp = address_parts[-1].split(", ")[1][-5:]

        except Exception:
            city = address_parts[-2].split(",")[0]
            state = address_parts[-2].split(", ")[1][0:2]
            zipp = address_parts[-2].split(", ")[1][-5:]

    if state == "Te":
        state = "TX"

    if address.split(" ")[-1] == "Redwood":
        address = address.replace(" Redwood", "")
        city = "Redwood City"

    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone_part = soup.text.strip().split("CONTACT")[1].split("Tel:")[1]
    except Exception:
        try:
            phone_part = soup.text.strip().split("CONTACT")[1].split("Phone:")[1]
        except Exception:
            try:
                phone_part = soup.text.strip().split("STORE INFO")[1].split("Phone:")[1]
            except Exception:
                try:
                    phone_part = (
                        soup.text.strip().split("CONTACT")[1].split("phone:")[1]
                    )
                except Exception:
                    try:
                        phone_part = (
                            soup.text.strip().split("CONTACT")[1].split("Phone")[1]
                        )
                    except Exception:
                        phone_part = "<MISSING>"

    x = 0
    phone = ""
    for character in phone_part:

        if bool(re.search(r"\d", character)) is True:
            x = x + 1
            phone = phone + character
            if x == 10:
                break

    location_type = "<MISSING>"
    longitude = response.split("!2d")[1].split("!3d")[0]
    latitude = response.split("!3d")[1].split("!")[0]

    hours_parts_maybe = soup.find_all("div", attrs={"class": "et_pb_text_inner"})

    for contender in hours_parts_maybe:
        if "hours" in contender.text.strip().lower():
            hours_parts = contender.text.strip().split("\n")[1:]
            break

    hours = ""
    for part in hours_parts:
        hours = hours + part + ", "

        if "Sun" in part:
            break

    hours = hours[:-2]

    if "coming soon" in hours.lower():
        continue

    city = (
        "".join([i for i in city if not i.isdigit()]).replace("=", "").replace("-", "")
    )

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
