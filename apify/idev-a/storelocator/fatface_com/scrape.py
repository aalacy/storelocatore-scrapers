import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json

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

    locator_domain = "https://www.fatface.com/"
    base_url = "https://www.fatface.com/stores"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("a.b-find-a-store-noresult__letter-store")
    for link in links:
        page_url = urljoin(
            "https://www.fatface.com",
            f"{link['href']}",
        )
        r1 = session.get(page_url)
        soup = bs(r1.text, "lxml")
        location = json.loads(
            soup.select_one("div.js-map-wrapper.b-find-a-store-map")["data-mapconfig"]
        )
        location_name = location["name"]
        store_number = location["id"]
        street_address = location["address1"] + myutil._valid1(
            location.get("address2", "")
        )
        city = myutil._valid(location["city"])
        zip = myutil._valid(location["postalCode"])
        state = myutil._valid(location["state"])
        country_code = location["countryCode"]
        phone = myutil._valid(location["phone"])
        location_type = "<MISSING>"
        latitude = location["latitude"]
        longitude = location["longitude"]
        hours_of_operation = "; ".join(
            [
                _["content"]
                for _ in soup.select("ul.b-store-locator-details__listing li")
            ]
        )

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
