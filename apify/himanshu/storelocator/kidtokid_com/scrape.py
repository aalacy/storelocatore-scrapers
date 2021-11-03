import csv
import json

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
    # Your scraper here
    session = SgRequests()

    items = []

    DOMAIN = "kidtokid.com"
    start_url = "https://kidtokid.com/global/gen/model/search?include_classes=sitefile,address&take=6000&class_string=location"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["data"]["models"]:
        store_url = "https://kidtokid.com/location/{}".format(poi["url"])
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["street_1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["address"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["zipcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        store_number = poi["location_id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["address"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["address"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = (
            poi["c_store-hours"].replace("\n", " ").replace("\t", " ").strip()
        )

        item = [
            DOMAIN,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zip_code,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
