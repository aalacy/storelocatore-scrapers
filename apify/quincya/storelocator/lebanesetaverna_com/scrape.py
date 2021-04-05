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

    base_links = [
        "https://www.lebanesetaverna.com/lebanese-taverna",
        "https://www.lebanesetaverna.com/leb-tav",
    ]

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    data = []

    for base_link in base_links:
        req = session.get(base_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find_all(class_="sqs-block html-block sqs-block-html")
        locator_domain = "lebanesetaverna.com"

        for item in items:
            if "PM" not in item.text.upper() and "temporarily" not in item.text:
                continue
            location_name = item.h4.text.strip()

            raw_data = list(item.stripped_strings)
            if "menu" in raw_data[-1].lower():
                raw_data.pop(-1)
            raw_address = (
                raw_data[1]
                .replace("Avenue, NW", "Avenue NW")
                .replace(", SUITE", " SUITE")
                .split(",")
            )

            street_address = raw_address[0]
            city = raw_address[1].strip()
            state = raw_address[-1].split()[0].strip()
            try:
                zip_code = raw_address[-1].split()[1].strip()
            except:
                zip_code = "<MISSING>"

            if state in city:
                city = street_address.split()[-1].strip()
                street_address = " ".join(street_address.split()[:-1])
                if city == "SPRING":
                    city = "SILVER SPRING"
                    street_address = street_address.replace("SILVER", "").strip()

            hours_of_operation = " ".join(raw_data[2:-1]).replace("\xa0", "")

            if "temporarily closed" in raw_data[-1]:
                hours_of_operation = "Temporarily Closed"
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            try:
                phone = re.findall(r"[0-9]{3}.[0-9]{3}.[0-9]{4}", str(item.text))[0]
            except:
                try:
                    phone = re.findall(r"[0-9]{3}-[0-9]{3}-[0-9]{4}", str(item))[0]
                except:
                    phone = "<MISSING>"

            latitude = "<MISSING>"
            longitude = "<MISSING>"

            data.append(
                [
                    locator_domain,
                    base_link,
                    location_name,
                    street_address.replace(",", ""),
                    city.replace(",", ""),
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
