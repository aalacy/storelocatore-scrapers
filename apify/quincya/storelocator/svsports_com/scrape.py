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

    base_link = "https://www.svsports.com/pages/our-locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="location-block")
    locator_domain = "svsports.com"

    for item in items:

        raw_address = list(item.find(class_="content-wrapper").stripped_strings)

        location_name = raw_address[0].split(":")[1].strip()
        street_address = raw_address[1].strip()
        city = item.h1.text.split(",")[0].strip()
        state = item.h1.text.split(",")[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = raw_address[-1].strip()

        map_str = item.a["href"]
        try:
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(
                ","
            )
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"

        if "38 N. West" in street_address:
            latitude = "40.4445187"
            longitude = "-75.3615462"
            zip_code = "18951"

        if "2913 Spooky" in street_address:
            zip_code = "17545"

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
