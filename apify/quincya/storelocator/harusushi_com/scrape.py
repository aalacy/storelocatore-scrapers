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

    base_link = "https://harusushi.com/location/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="locations").find_all(class_="one_third")

    data = []

    locator_domain = "harusushi.com"

    for item in items:
        if item.find(class_="location-address").text:
            location_name = item.h3.text.strip()
            raw_address = (
                item.find(class_="location-address")
                .text.replace("Street, Un", "Street Un")
                .split(",")
            )

            street_address = raw_address[0].strip()
            city = raw_address[1].strip().split(",")[0].strip()
            state = raw_address[-1].strip().split()[0].strip()
            zip_code = raw_address[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            try:
                phone = item.find(class_="location-phone").text.strip()
                if not phone:
                    phone = "<MISSING>"
            except:
                phone = "<MISSING>"

            link = item.find(class_="location-link").a["href"]
            if "http" not in link:
                link = "https://harusushi.com" + link

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", str(base))[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            try:
                hours_of_operation = " ".join(
                    list(base.find(class_="hours-wrapper").stripped_strings)
                )
            except:
                hours_of_operation = "<MISSING>"

            data.append(
                [
                    locator_domain,
                    link,
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
