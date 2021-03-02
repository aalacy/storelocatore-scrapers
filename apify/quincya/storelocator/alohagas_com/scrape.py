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

    base_link = "https://www.alohagas.com/aloha-gas/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    found_poi = []
    final_links = []

    locator_domain = "alohagas.com"

    items = base.find(id="el-195f73c9").find_all("a")

    for item in items:
        main_link = "https://www.alohagas.com" + item["href"]
        req = session.get(main_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        next_items = base.find_all(class_="locationItem")

        for next_item in next_items:
            link = "https://www.alohagas.com" + next_item.a["href"]
            if link not in final_links:
                final_links.append(link)

    for final_link in final_links:
        req = session.get(final_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find_all("div", {"class": re.compile(r"locationIte.+")})
        for item in items:
            raw_data = item.div.find_all("div")

            location_name = item.h3.text.strip()
            if location_name in found_poi:
                continue
            found_poi.append(location_name)

            street_address = raw_data[0].text.strip()
            if street_address[-1:] == ",":
                street_address = street_address[:-1].strip()
            city_line = raw_data[1].text.strip().split(",")
            city = city_line[0].strip()
            state = city_line[-1].strip().split()[0].strip()
            zip_code = city_line[-1].strip().split()[1].strip()
            country_code = "US"
            store_number = "<MISSING>"

            location_type = ""
            raw_types = item.find_all(style="font-weight: bold;")
            for raw_type in raw_types:
                location_type = (location_type + ", " + raw_type.text.strip()).strip()
            location_type = location_type[1:].strip()
            if not location_type:
                location_type = "<MISSING>"

            phone = raw_data[2].text.strip()
            if not phone:
                phone = "<MISSING>"
            hours_of_operation = (
                raw_data[3].text.replace("*", "").replace("pm", "pm ").strip()
            )
            latitude = "<MISSING>"
            longitude = "<MISSING>"

            data.append(
                [
                    locator_domain,
                    final_link,
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
