import csv
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

    base_link = "https://www.foodgiant.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="store-list-row-container store-bucket filter-rows")
    locator_domain = "foodgiant.com"

    for item in items:
        location_name = (
            item.find(class_="store-name")["data-state"]
            + " "
            + item.find(class_="store-name").text
        )
        if "food giant" not in location_name.lower():
            continue
        raw_address = list(item.find(class_="store-address").stripped_strings)
        street_address = raw_address[0].strip()
        city_line = raw_address[-1].split(",")
        city = city_line[0].strip()
        state = city_line[1][:-6].strip()
        zip_code = raw_address[-1][-6:].strip()
        country_code = "US"
        store_number = item.find(class_="store-number").text.strip()
        location_type = "<MISSING>"
        phone = item.find(class_="store-phone").text.split("--")[0].strip()
        hours_of_operation = (
            item.find(class_="store-list-row-item-col02").get_text(" ").strip()
        )
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"
        map_str = item.find_all(class_="block-link")[-1]["href"]
        geo = re.findall(r"[0-9]{2,3}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(
            ","
        )
        latitude = geo[0]
        longitude = geo[1]

        data.append(
            [
                locator_domain,
                base_link,
                location_name,
                street_address,
                city,
                state,
                zip_code,
                country_code,
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
