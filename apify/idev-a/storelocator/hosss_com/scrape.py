import csv
from bs4 import BeautifulSoup as bs
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


def _headers():
    return {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,ko;q=0.8",
        "referer": "https://veggiegrill.com/",
        "cache-control": "max-age=0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }


def fetch_data():
    locator_domain = "https://hosss.com/locations-hours/"
    base_url = "https://hosss.com/wp-admin/admin-ajax.php?action=store_search&lat=40.7127753&lng=-74.0059728&max_results=100&search_radius=500"
    r = session.get(base_url, headers=_headers())
    locations = json.loads(r.text)
    data = []
    for location in locations:
        page_url = "<MISSING>"
        store_number = myutil._valid(location["id"])
        location_name = location["store"]
        street_address = myutil._valid(
            f"{location.get('address')} {location.get('address2')}"
        )
        city = myutil._valid(location.get("city"))
        state = myutil._valid(location.get("state"))
        zip = myutil._valid(location.get("zip"))
        country_code = myutil.get_country_by_code(state)
        phone = myutil._valid(location.get("phone"))
        location_type = "<MISSING>"
        latitude = myutil._valid(location.get("lat"))
        longitude = myutil._valid(location.get("lng"))
        tags = bs(location["hours"], "lxml")
        hours = []
        for tag in tags.select("tr"):
            hours.append(f"{tag.td.text}: {tag.select_one('td time').text}")
        hours_of_operation = "; ".join(hours)

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
