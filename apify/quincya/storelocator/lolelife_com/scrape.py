import csv
import json
import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    session = SgRequests()

    base_link = "https://www.lolelife.com/store-locator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "lolelife.com"

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "stores:{CA" in str(script):
            script = str(script)
            break

    js = script.split("stores:")[1].split("}],EU")[0] + "}]}"
    js = (js.replace("{", '"{"').replace(",", '","').replace('"["', "["))[1:]
    js = (
        (re.sub(r"(\D:)", r'\1"', js))
        .strip()
        .replace(':"', '":"')
        .replace('"""', '"')
        .replace('""', '"')
        .replace('"["', "[")
        .replace('}]",', '"}],')
        .replace('day","', "day")
        .replace(' AM","', " AM")
        .replace(' PM","', " PM")
        .replace(':30","', ":30")
        .replace(':00","', ":00")
        .replace('24 hours","', "24 hours")
        .replace("Mcountry", 'M" ,"country')
        .replace("hourscountry", 'hours" ,"country')
        .replace('}","{', "},{")
        .replace("},{", '"},{')
        .replace('""', '"')
        .replace('FLOOR","', "FLOOR")
        .replace('PRINCIPALE","', "PRINCIPALE")
        .replace('"," Unit', " Unit")
        .replace('"," UNIT', " UNIT")
        .replace('"," ca","longi', ', ca","longi')
        .replace('"," CA","', ', CA","')
        .replace('stone"," co', "stone, co")
        .replace('stone"," CO', "stone, CO")
        .replace('"," ut ', ", ut ")
    )
    store_data = json.loads(js)

    for country in store_data:
        stores = store_data[country]
        for store in stores:
            location_name = store["name_store"].replace("dk", "Lole")
            street_address = store["address"]
            city = "<MISSING>"
            state = "<MISSING>"

            if "Toronto" in location_name:
                city = "Toronto"
            if "Northville" in location_name:
                city = "Northville"
            if "Lolë" in location_name and "Livia" not in location_name:
                city = (
                    " ".join(location_name.split("Lolë")[1:])
                    .replace("M&V", "")
                    .replace("M&V", "")
                    .replace("17th Ave", "")
                    .replace("Ste-Catherine", "")
                    .strip()
                )

            if "Keystone, CO" in city:
                city = "Keystone"
                state = "CO"

            if "Tahoe, CA" in city:
                city = "Tahoe"
                state = "CA"

            zip_code = store["postalcode"].replace("TOE 1E0", "T0E 1E0")
            if len(zip_code) < 3:
                zip_code = "<MISSING>"
            store_number = store["id"]
            location_type = "<MISSING>"
            phone = store["phone"]
            if len(phone) < 5:
                phone = "<MISSING>"

            hours_of_operation = store["weekday"]
            if len(hours_of_operation) < 20:
                hours_of_operation = "<MISSING>"

            latitude = store["latitude"]
            longitude = store["longitude"]

            data.append(
                [
                    locator_domain,
                    "https://www.lolelife.com/store-locator",
                    location_name,
                    street_address,
                    city,
                    state,
                    zip_code,
                    country,
                    store_number,
                    phone,
                    location_type,
                    latitude,
                    longitude,
                    hours_of_operation,
                ]
            )
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
