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

    base_link = "https://ao.com/store-locator"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    data = []

    items = base.find_all(class_="ao-cta-blue")
    locator_domain = "ao.com"

    for item in items:
        link = "https://ao.com" + item["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        raw_address = list(
            base.find(
                class_="details-inner text-body-sm text-secondary"
            ).p.stripped_strings
        )[2:]

        location_name = base.h2.text.strip()
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[2].strip()
        try:
            zip_code = raw_address[3].strip()
        except:
            zip_code = state
            state = "<MISSING>"

        country_code = "UK"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = "<MISSING>"
        hours_of_operation = " ".join(
            list(
                base.find(class_="details-inner text-body-sm text-secondary")
                .find_all("p")[1]
                .stripped_strings
            )[1:]
        )
        map_str = base.find(class_="ao-cta-blue")["href"]
        geo = re.findall(r"[0-9]{2,3}\.[0-9]+,-[0-9]{1,2}\.[0-9]+", map_str)[0].split(
            ","
        )
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
