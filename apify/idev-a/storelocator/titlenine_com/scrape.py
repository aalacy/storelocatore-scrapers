import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
from sgscrape.sgpostal import parse_address_usa
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
        try:
            store_number = "<MISSING>"
            location_name = location["name"]
            country_code = "US"
            soup1 = bs(location["infoWindowHtml"], "lxml")
            block = [_ for _ in soup1.select_one(".store-data").stripped_strings]
            page_url = urljoin(
                "https://www.titlenine.com", soup1.select_one("a.store-info")["href"]
            )
            _address = " ".join([_.strip() for _ in block[0].split("\n") if _.strip()])
            if len(_address.split("/")) > 1:
                _address = _address.split("/")[1]
            addr = parse_address_usa(_address)
            street_address = addr.street_address_1.replace(
                "Hilldale Shopping Center", ""
            )
            city = addr.city
            state = addr.state
            zip = addr.postcode
            phone = block[1]
            location_type = "<MISSING>"
            latitude = location["latitude"]
            longitude = location["longitude"]
            hours_of_operation = "; ".join(
                [
                    _
                    for _ in soup1.select_one(
                        "div.store-info-section p"
                    ).stripped_strings
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

            myutil._check_duplicate_by_loc(data, _item)
        except:
            import pdb

            pdb.set_trace()

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
