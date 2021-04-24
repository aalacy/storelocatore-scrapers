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

    base_link = "https://www.doncuco.com/order-online-1"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []
    locator_domain = "doncuco.com"

    items = base.find_all(class_="font_2")
    for item in items:
        link = item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = " ".join(
            list(base.find_all(class_="_1Z_nJ")[1].stripped_strings)
        )

        raw_address = (
            base.find_all(class_="_1Z_nJ")[2]
            .text.split("\u200b")[1]
            .replace("ADDRESS", "")
            .replace("Ave.", "Ave.\n")
            .strip()
            .split("\n")
        )
        street_address = raw_address[0]
        city_line = raw_address[1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        phone = (
            base.find_all(class_="_1Z_nJ")[2]
            .text.split("\u200b")[2]
            .replace("\n", " ")
            .split(":")[1]
            .split()[0]
            .strip()
        )
        try:
            hours_of_operation = (
                base.find_all(class_="_1Z_nJ")[2]
                .text.split("\u200b")[0]
                .replace("HOURS", "")
                .replace("\n", " ")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"

        map_str = base.find_all(class_="_1Z_nJ")[2].a["href"]
        geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(",")
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
