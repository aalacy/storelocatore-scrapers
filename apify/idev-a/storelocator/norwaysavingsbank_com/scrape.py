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
    data = []

    locator_domain = "https://www.norwaysavings.bank/"
    base_url = "https://www.norwaysavings.bank/wp-admin/admin-ajax.php?action=store_search&lat=44.21396&lng=-70.54481&max_results=100&search_radius=100&autoload=1"
    r = session.get(base_url)
    items = json.loads(r.text)
    for item in items:
        page_url = item["permalink"]
        location_name = item["store"].replace("<strong>", "").replace("</strong>", "")
        street_address = myutil._valid(item["address"] + " " + item["address2"])
        city = item["city"]
        state = item["state"]
        zip = item["zip"]
        country_code = item["country"]
        phone = myutil._valid(item.get("phone", ""))
        store_number = item["id"]
        location_type = "<MISSING>"
        latitude = item["lat"]
        longitude = item["lat"]
        hours = [
            _.text.strip() for _ in bs(item["location_lobby_hours"], "lxml").select("p")
        ]
        hours_of_operation = myutil._valid("; ".join(hours))
        if "closed" in hours_of_operation.lower():
            hours_of_operation = "Closed"
        else:
            for hour in hours:
                if hour.startswith("Lobby:"):
                    hours_of_operation = "; ".join(
                        hour.replace("Lobby:", "").split("\n")
                    )
                    break

        hours_of_operation = myutil._valid(hours_of_operation) or "<MISSING>"

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

        data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
