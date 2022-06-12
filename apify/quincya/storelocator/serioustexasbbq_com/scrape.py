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

    base_link = "https://www.serioustexasbbq.com/locations.php"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="locationBox")
    locator_domain = "serioustexasbbq.com"

    for item in items:

        raw_data = list(item.stripped_strings)

        location_name = "<MISSING>"

        street_address = raw_data[0].strip()
        street_address = (re.sub(" +", " ", street_address)).strip()
        city_line = raw_data[1].strip().replace("rado, 8", "rado 8").split(",")
        city = city_line[0].strip()
        state = city_line[1][:-6].strip()
        zip_code = city_line[1][-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_data[2].strip()

        hours_of_operation = ""
        raw_hours = raw_data[-2:]
        for hours in raw_hours:
            if "pm" in hours:
                hours_of_operation = (
                    hours_of_operation
                    + " "
                    + hours.replace("Map and Directions", "").strip()
                ).strip()
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = "<MISSING>"
        longitude = "<MISSING>"

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
