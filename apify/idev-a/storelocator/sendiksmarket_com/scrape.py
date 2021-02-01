import csv
from sgrequests import SgRequests
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
    locator_domain = "https://www.sendiks.com/"
    base_url = "https://api.freshop.com/1/stores?app_key=sendiks&has_address=true&limit=-1&token=d4e5be6cc9f62cad0d0e126beb352c8b"
    r = session.get(base_url)
    locations = json.loads(r.text)["items"]
    data = []
    for location in locations:
        page_url = location["url"]
        location_name = location["name"]
        country_code = "US"
        zip = location["postal_code"]
        city = location["city"]
        state = location["state"]
        if "address_1" in location:
            street_address = myutil._valid(location["address_1"])
        else:
            street_address = location["address_0"]

        phone = "<MISSING>"
        if "phone_md" in location:
            phone = location["phone_md"]
        elif "phone" in location:
            phone = location["phone"]

        store_number = location["store_number"]
        location_type = "<MISSING>"
        latitude = location["latitude"]
        longitude = location["longitude"]
        hours_of_operation = "<MISSING>"
        if "hours_md" in location:
            hours_of_operation = location["hours_md"]
        elif "hours" in location:
            hours_of_operation = location["hours"]
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
