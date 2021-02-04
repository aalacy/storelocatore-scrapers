import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
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


def parse_detail(data, base_url, locator_domain, country):
    rr = session.get(base_url)
    soup = bs(rr.text, "lxml")
    map_canvas = soup.select_one("div.map-canvas")["data-locations"]
    locations = json.loads(map_canvas)
    for location in locations:
        page_url = f'{locator_domain}en/store-detail?lang=en&sid={location["id"]}'
        rr1 = session.get(page_url)
        soup1 = bs(rr1.text, "lxml")
        store_number = location["id"]
        location_name = location["name"]
        country_code = country
        address = myutil._strip_list(
            soup1.select_one(
                "div.store-details a.store-address address.address"
            ).text.split("\n")
        )
        street_address = " ".join(address[:-2])
        city = myutil._valid(address[-2].replace(",", ""))
        state = "<MISSING>"
        zip = myutil._valid(address[-1])
        _phone = soup1.select_one("div.store-details a.phone")
        phone = "<MISSING>"
        if _phone:
            phone = myutil._valid(_phone["href"].replace("tel:", ""))
        location_type = "<MISSING>"
        closed = soup1.select_one("div.store-details div.live-open")
        hours_of_operation = "<MISSING>"
        if closed and closed.text.strip() == "Closed":
            location_type = "Closed"
        else:
            _hours = soup1.select("#store-hours div.store-hour-box")
            hours = []
            for _ in _hours:
                hours.append(
                    f'{_.h5.text.strip()}: {_.select_one("span").text.strip()}'
                )
            hours_of_operation = "; ".join(hours) or "<MISSING>"

        latitude = location["latitude"]
        longitude = location["longitude"]

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


def fetch_data():
    data = []

    # canada
    locator_domain = "https://ca.diesel.com/"
    base_url = "https://ca.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "CA")

    # uk
    locator_domain = "https://uk.diesel.com/"
    base_url = "https://uk.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "UK")

    # us
    locator_domain = "https://shop.diesel.com/"
    base_url = "https://shop.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "US")

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
