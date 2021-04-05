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
    base_url = "https://storesservice.o2.co.uk/stores/v2/near?latitude=51.5073509&longitude=-0.1277583&maxStores=10000"
    r = session.get(base_url)
    items = json.loads(r.text)
    data = []
    for item in items:
        page_url = base_url
        location_name = item["name"]
        street_address = myutil._valid_uk(
            f"{item['address']['address1']} {item['address'].get('address2', '')}"
        )
        city = myutil._valid_uk(item["address"]["address4"])
        state = myutil._valid_uk(item["address"]["county"])
        zip = myutil._valid_uk(item["address"]["postcode"])
        country_code = "UK"
        store_number = item["id"]
        phone = myutil._valid_uk(item["contactDetails"].get("telephoneNumber"))
        location_type = myutil._valid_uk(item["franchiseGroup"])
        latitude = item["location"]["latitude"]
        longitude = item["location"]["longitude"]
        hours_of_operation = "; ".join(
            [f'{h["dayOfWeek"]} {h["open"]}-{h["close"]}' for h in item["openingTimes"]]
        )

        _item = [
            "https://www.o2.co.uk/",
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
