import csv
import json
from sgrequests import SgRequests

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
    base_url = "https://www.danielsjewelers.com"
    r = session.get(
        "https://www.danielsjewelers.com/storelocator/index/stores?type=all"
    )
    store_list = json.loads(r.text)["storesjson"]
    data = []
    for store in store_list:
        page_url = (
            "https://www.danielsjewelers.com/storelocator/index/details?locatorId="
            + store["storelocator_id"]
        )
        detail_url = (
            "https://www.danielsjewelers.com/storelocator/index/Storedetail?locatorId="
            + store["storelocator_id"]
        )
        r1 = session.get(detail_url)
        store_detail = json.loads(r1.text)["storesjson"][0]

        hours_of_operation = (
            "Sun: "
            + myutil.parseHour(store_detail["sunday_open"])
            + " - "
            + myutil.parseHour(store_detail["sunday_close"])
        )
        hours_of_operation += (
            " Mon: "
            + myutil.parseHour(store_detail["monday_open"])
            + " - "
            + myutil.parseHour(store_detail["monday_close"])
        )
        hours_of_operation += (
            " Tue: "
            + myutil.parseHour(store_detail["tuesday_open"])
            + " - "
            + myutil.parseHour(store_detail["tuesday_close"])
        )
        hours_of_operation += (
            " Wed: "
            + myutil.parseHour(store_detail["wednesday_open"])
            + " - "
            + myutil.parseHour(store_detail["wednesday_close"])
        )
        hours_of_operation += (
            " Thu: "
            + myutil.parseHour(store_detail["thursday_open"])
            + " - "
            + myutil.parseHour(store_detail["thursday_close"])
        )
        hours_of_operation += (
            " Fri: "
            + myutil.parseHour(store_detail["friday_open"])
            + " - "
            + myutil.parseHour(store_detail["friday_close"])
        )
        hours_of_operation += (
            " Sat: "
            + myutil.parseHour(store_detail["saturday_open"])
            + " - "
            + myutil.parseHour(store_detail["saturday_close"])
        )

        store_number = store["store_code"]
        location_name = store["store_name"]
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip = store["zipcode"]
        country_code = store["country_id"]
        phone = store["phone"]
        location_type = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]

        data.append(
            [
                base_url,
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
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
