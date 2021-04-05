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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "lloydspharmacy.com"
    start_url = "https://store-locator.lloydspharmacy.com/store-locator"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["stores"]:
        store_url = "<MISSING>"
        location_type = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING"
        street_address = poi["address"]["street"]
        city = poi["address"]["town"]
        city = city if city else "<MISSING>"
        state = poi["address"]["county"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postcode"]
        country_code = poi["address"]["country"]
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        latitude = poi["location"]["lat"]
        longitude = poi["location"]["lng"]
        hours_of_operation = []
        for day, hours in poi["hours"].items():
            if hours:
                opens = hours[0]
                closes = hours[1]
                hours_of_operation.append(f"{day} {opens} - {closes}")
            else:
                hours_of_operation.append(f"{day} closed")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
