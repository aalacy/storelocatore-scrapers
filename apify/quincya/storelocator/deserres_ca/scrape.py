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

    base_link = "https://www.deserres.ca/en/find-a-store"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    sections = base.find_all(class_="accordion_item")
    locator_domain = "deserres.ca"

    for section in sections:
        state = section.find(class_="accordion_item-title").text.strip()
        items = section.find_all("li")

        for item in items:
            link = item.a["href"]
            location_name = item.a.text.split(">")[0].strip()

            raw_address = list(item.stripped_strings)[1:]
            street_address = raw_address[0]
            city = " ".join(raw_address[-1].split()[2:]).strip()
            zip_code = " ".join(raw_address[-1].split()[:2]).strip()
            country_code = "CA"
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            try:
                phone = re.findall(
                    r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(base.address.text)
                )[0]
            except:
                phone = "<MISSING>"

            try:
                hours_of_operation = " ".join(
                    list(base.find(class_="hours").dl.stripped_strings)
                )
            except:
                if "temporarily closed" in base.text:
                    hours_of_operation = "Temporarily Closed"
                else:
                    hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
