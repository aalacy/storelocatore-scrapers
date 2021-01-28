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


def fetch_data():
    locator_domain = "http://presidentesupermarkets.com/category/locations/"
    base_url = "http://presidentesupermarkets.com/wp-admin/admin-ajax.php?lang=en&action=store_search&lat=0&lng=0&max_results=100&search_radius=500&autoload=1"
    r = session.get(base_url)
    items = json.loads(r.text)
    data = []
    for item in items:
        page_url = "<MISSING>"
        location_name = item["store"]
        street_address = myutil._valid(f"{item['address']} {item.get('address2', '')}")
        city = myutil._valid(item["city"])
        state = myutil._valid(item["state"])
        zip = myutil._valid(item["zip"])
        country_code = "US"
        store_number = item["id"]
        phone = myutil._valid(item.get("phone"))
        location_type = "<MISSING>"
        latitude = item["lat"]
        longitude = item["lng"]
        tags = bs(item["hours"], "lxml")
        hours_of_operation = "; ".join(
            [f'{h.td.text}: {h.select_one("td time").text}' for h in tags.select("tr")]
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

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
