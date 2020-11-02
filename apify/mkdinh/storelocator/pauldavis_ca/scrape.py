import re
import csv
from sgrequests import SgRequests

MISSING = "<MISSING>"
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def write_output(data):
    with open("data.csv", "w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "store_number",
                "location_type",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "latitude",
                "longitude",
                "phone",
                "hours_of_operation",
            ]
        )

        for record in data:
            writer.writerow(record)


def get(obj, key):
    value = obj.get(key)
    is_placeholder = re.search("\[.*\]", str(value))

    return value if not is_placeholder else MISSING


def fetch_data():
    locator_domain = "pauldavis.ca"
    page_url = "https://pauldavis.ca/wp-json/locator/v1/list"
    locations = session.get(page_url, headers=headers).json()

    for location in locations:
        location_name = get(location, "name")
        store_number = get(location, "id",)
        latitude = get(location, "lat")
        longitude = get(location, "lng")
        street_address = get(location, "address")
        city = get(location, "city")
        state = get(location, "state")
        zipcode = get(location, "postal")
        phone = get(location, "phone")
        country_code = "CA"

        location_type = MISSING
        hours_of_operation = MISSING

        yield [
            locator_domain,
            page_url,
            location_name,
            store_number,
            location_type,
            street_address,
            city,
            state,
            zipcode,
            country_code,
            latitude,
            longitude,
            phone,
            hours_of_operation,
        ]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
