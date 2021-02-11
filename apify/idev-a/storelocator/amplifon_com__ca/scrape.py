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


def _headers():
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "csrf-token": "undefined",
        "Origin": "https://www.amplifon.com",
        "Referer": "https://www.amplifon.com/ca/branch-locator/amplifon-store-map?addr=Toronto_-ON_-Canada&lat=43.653226&long=-79.3831843",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }


def _data():
    return {
        "countryCode": "CA",
        "latitude": "43.653226",
        "longitude": "-79.3831843",
        "locale": "en_CA",
        "limit": 1500,
        "radius": 80000,
        "type": "",
    }


def fetch_data():
    data = []

    locator_domain = "https://www.amplifon.com/ca"
    base_url = "https://www.amplifon.com/ca/branch-locator/amplifon-store-map.getStores.json?addr=Toronto_-ON_-Canada&lat=43.653226&long=-79.3831843"
    rr = session.post(base_url, headers=_headers(), data=_data())
    locations = json.loads(rr.text)
    for location in locations:
        page_url = f'https://www.amplifon.com/ca/branch-locator/hearing-clinics-{"-".join(myutil._strip_list(location["city"].split("-")))}-{location["state"]}/{location["shortName"]}-{location["type"]}{location["shopNumber"]}'
        store_number = location["shopNumber"]
        location_name = myutil._valid(location["shopName"])
        country_code = location["country"]
        street_address = location["address"]
        city = location["city"]
        state = location["state"]
        zip = location["cap"]
        phone = "<MISSING>"
        if location["phones"]:
            phone = myutil._valid(location["phones"][0]["phonenumber"])
        location_type = location["type"]
        latitude = location["latitude"]
        longitude = location["longitude"]
        rr = session.get(page_url)
        soup1 = bs(rr.text, "lxml")
        hours = []
        for _ in soup1.select("#detailStoreInfo div.ds-list-week p.ds-single-day"):
            hours.append(
                f'{_.select_one("span.ds-day").text}: {_.select_one("span.ds-time").text}'
            )
        hours_of_operation = myutil._valid("; ".join(hours))

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
