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


def _headers():
    return {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json",
        "X-OnAir-ClientAppKey": "329a4b47-48a3-4b90-8de2-36aa62cdfe34",
        "country": "uk",
        "Host": "mobileb2c.amplifon.com",
        "Origin": "https://www.amplifon.com",
        "Referer": "https://www.amplifon.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    }


def _data():
    return {
        "countryCode": "021",
        "latitude": "53.79778169999999",
        "longitude": "-1.5413658",
        "locale": "en_GB",
        "limit": 1500,
        "radius": 10000,
        "type": "",
    }


def fetch_data():
    data = []

    locator_domain = "https://www.amplifon.com/uk"
    base_url = (
        "https://mobileb2c.amplifon.com/onstage-pa-s-mc/store-locator/v2/getStores"
    )
    rr = session.post(base_url, headers=_headers(), json=_data())
    locations = json.loads(rr.text)
    for location in locations:
        page_url = f'https://www.amplifon.com/uk/store-locator/hearing-aids-{location["normalizedProvince"]}/{location["shortName"]}-{location["type"]}{location["shopNumber"]}'
        store_number = location["shopNumber"]
        location_name = myutil._valid(location["shopName"])
        country_code = "UK"
        street_address = location["address"]
        city = location["city"]
        state = "<MISSING>"
        zip = location["cap"]
        phone = myutil._valid(location["phoneNumber1"])
        if phone == "<MISSING>":
            phone = myutil._valid(location.get("phoneNumber2"))
        location_type = location["type"]
        hours_of_operation = "<MISSING>"
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


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
