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

    base_link = "https://www.kwik-fit.com/locate-a-centre"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find(class_="lac_our-centres").find_all("a")
    locator_domain = "kwik-fit.com"

    for item in items:
        link = "https://www.kwik-fit.com" + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(base.find("address").stripped_strings)

        location_name = base.h1.text.strip()
        street_address = raw_address[0].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]

        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        zip_code = city_line[-1].strip()
        state = "<MISSING>"
        if len(city_line) == 3:
            state = city_line[1].strip()
        country_code = "UK"
        store_number = "<MISSING>"
        location_type = "Open"
        phone = raw_address[2]

        if "temporarily closed" in base.text:
            location_type = "Temporarily Closed"

        try:
            hours_of_operation = (
                " ".join(
                    list(
                        base.find(
                            class_="table table-bordered table-condensed table-striped table-hover"
                        ).stripped_strings
                    )
                )
                .replace("Day Opening Closing", "")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"
        map_str = base.find(
            class_="btn btn-kf btn-sm btn-kf-orange btn-select-centre btn-block"
        )["href"]

        try:
            geo = re.findall(r"[0-9]{2,3}\.[0-9]+,-[0-9]{1,2}\.[0-9]+", map_str)[
                0
            ].split(",")
        except:
            geo = re.findall(r"[0-9]{2,3}\.[0-9]+,[0-9]{1,2}\.[0-9]+", map_str)[
                0
            ].split(",")
        latitude = geo[0]
        longitude = geo[1]

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
