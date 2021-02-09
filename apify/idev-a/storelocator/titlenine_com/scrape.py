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

    locator_domain = "https://www.titlenine.com/"
    base_url = "https://www.titlenine.com/all-stores"
    rr = session.get(base_url)
    soup = bs(rr.text, "lxml")
    locations = json.loads(soup.select_one("div.map-canvas")["data-locations"])
    for location in locations:
        store_number = "<MISSING>"
        location_name = location["name"]
        country_code = "US"
        soup1 = bs(location["infoWindowHtml"], "lxml")
        block = [_ for _ in soup1.select_one(".store-data").stripped_strings]
        page_url = urljoin(
            "https://www.titlenine.com", soup1.select_one("a.store-info")["href"]
        )
        street_address = " ".join(
            myutil._strip_list(" ".join(block[0].split(",")[:-1]).strip().split("\n"))[
                :-1
            ]
        )
        city = block[0].split(",")[-2].strip().split("\n")[-1].strip()
        state = block[0].split(",")[-1].strip().split("\n")[0].strip()
        zip = block[0].split(",")[-1].strip().split("\n")[-1].strip()
        phone = block[1]
        location_type = "<MISSING>"
        latitude = location["latitude"]
        longitude = location["longitude"]
        hours_of_operation = block[-1]

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
