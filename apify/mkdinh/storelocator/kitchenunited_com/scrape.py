import csv
import random
import xmltodict
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


def fetch_data():
    locator_domain = "kitchenunited.com"
    page_url = f"https://runner.kitchenunited.com/api/restaurants?{random.random()}"

    data = session.get(page_url, headers=headers).json()

    for restaurant in data["restaurants"]:
        location_name = restaurant.get("name", MISSING)
        store_number = restaurant.get("id",)
        latitude = restaurant.get("latitude", MISSING)
        longitude = restaurant.get("longitude", MISSING)
        street_address = restaurant.get("streetaddress", MISSING)
        city = restaurant.get("city", MISSING)
        state = restaurant.get("state", MISSING)
        zipcode = restaurant.get("zip", MISSING)
        phone = restaurant.get("telephone", MISSING)
        country_code = restaurant.get("country", MISSING)

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
