import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin

from util import Util  # noqa: I900

myutil = Util()


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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
    data = []

    locator_domain = "https://www.chevys.com/"
    base_url = "https://www.chevys.com/locations/"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("#content section.content-module.locations div.location")
    for link in links:
        page_url = urljoin(
            "https://www.chevys.com",
            f"{link.h2.a['href']}",
        )
        location_name = link.h2.a.text.strip()
        store_number = link["data-location-id"]
        direction = (
            link.select_one("div.location-links a")["href"]
            .split("destination=")[1]
            .strip()
            .split(",")
        )
        latitude = direction[0]
        longitude = direction[1]
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        hours = []
        for _ in soup1.select(".hours .hours--detail"):
            hours.append(f"{_.select_one('.day').text}: {_.select_one('.hours').text}")

        hours_of_operation = "; ".join(hours)
        address = [
            _ for _ in soup1.select_one("div.location-address a").stripped_strings
        ]
        street_address = address[0]
        city = address[1].split(",")[0]
        state = address[1].split(",")[1].strip()
        zip = "<MISSING>"
        country_code = myutil.get_country_by_code(state)
        location_type = "<MISSING>"
        phone = soup1.select_one("div.location-contact p a").text
        _item = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
