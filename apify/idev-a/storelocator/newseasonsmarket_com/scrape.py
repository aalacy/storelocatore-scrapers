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


def _phone(phone):
    if phone:
        return phone.split("\n")[0].strip().replace("Phone:", "")
    else:
        return "<MISSING>"


def fetch_data():
    data = []

    locator_domain = "https://www.newseasonsmarket.com/"
    base_url = "https://www.newseasonsmarket.com/wp-admin/admin-ajax.php?action=get-stores-with-extras&terms=&lat=45.512&lng=-122.679"
    rr = session.get(base_url)
    locations = json.loads(rr.text)
    for id in locations:
        location = locations[id]
        page_url = location["permalink"]
        store_number = id.split("-")[1]
        location_name = location["title"]
        country_code = "US"
        street_address = location["address"]
        city = location["city"]
        state = location["state"]
        r1 = session.get(page_url)
        soup = bs(r1.text, "lxml")
        addr = [
            _
            for _ in soup.select_one("div.chalkboard-hoursandaddress").stripped_strings
        ][:-1]
        zip = addr[1].split(",")[1].strip().split(" ")[1].strip()
        phone = myutil._valid(location["phone"])
        location_type = "<MISSING>"
        latitude = location["lat"]
        longitude = location["lng"]
        hours_of_operation = myutil._valid(location.get("hours") + " (daily)")

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
