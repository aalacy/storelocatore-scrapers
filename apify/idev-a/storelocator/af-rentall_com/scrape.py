import csv
from sgrequests import SgRequests
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


def _phone(phone):
    if phone:
        return phone.split("\n")[0].strip().replace("Phone:", "")
    else:
        return "<MISSING>"


def fetch_data():
    data = []

    locator_domain = "https://af-rentall.com/"
    base_url = "https://af-rentall.com/index.php?mact=Locations,cntnt01,searchresults,0&cntnt01showtemplate=false&cntnt01returnid=44&cntnt01zipcode=&cntnt01distance=25"
    rr = session.get(base_url)
    locations = json.loads(rr.text)
    for location in locations:
        page_url = urljoin("https://af-rentall.com", location.get("url"))
        store_number = location["id"].strip()
        location_name = myutil._valid(location["name"])
        country_code = "US"
        street_address = location["address"] + myutil._valid1(location["address2"])
        city = location["city"]
        state = location["state"]
        zip = location["zipcode"]
        phone = myutil._valid(location["phone"])
        location_type = "<MISSING>"
        latitude = location["latitude"]
        longitude = location["longitude"]
        hours_of_operation = myutil._valid(
            ";".join(location.get("store_hours").split("<br>"))
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
