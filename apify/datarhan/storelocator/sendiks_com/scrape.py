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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "sendiks.com"
    start_url = "https://api.freshop.com/1/stores?app_key=sendiks&has_address=true&limit=-1&token=d6144ff1999262e13d75f59c3334d615"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["items"]:
        store_url = poi.get("url")
        if not store_url:
            continue
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi.get("address_1")
        if not street_address:
            street_address = poi["address_0"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi.get("phone_md")
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi.get("hours_md")
        hours_of_operation = hours_of_operation if hours_of_operation else "<MISSING>"

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
