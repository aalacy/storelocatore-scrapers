import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import json
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

    locator_domain = "https://elahorro.net/"
    base_url = "https://elahorro.net/es/tiendas"
    rr = session.get(base_url)
    locations = json.loads(
        rr.text.split(',"features":')[1]
        .strip()
        .split(',"pagination":null};')[0]
        .strip()
    )
    for location in locations:
        page_url = urljoin("https://elahorro.net", location["properties"]["url"])
        store_number = location["id"]
        location_name = location["properties"]["name"]
        country_code = "US"
        address = [
            _
            for _ in bs(location["properties"]["fulladdress"], "lxml")
            .select_one(".locationaddress")
            .stripped_strings
        ]
        street_address = address[0]
        city = address[1].split(",")[0]
        state = address[1].split(",")[1].strip()
        zip = address[2].split("\xa0")[-1]
        phone = "<MISSING>"
        location_type = location["type"]
        latitude = location["geometry"]["coordinates"][1]
        longitude = location["geometry"]["coordinates"][0]
        hours_of_operation = "<MISSING>"

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

        myutil._check_duplicate_by_loc(data, _item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
