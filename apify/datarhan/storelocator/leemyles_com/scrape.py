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

    DOMAIN = "leemyles.com"
    start_url = "https://www.leemyles.com/api/json/places/get"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["places"]["locations"]:
        store_url = poi["url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["entry"]["title"]
        street_address = poi["postalAddress"]["street"]
        city = poi["postalAddress"]["city"]
        state = poi["postalAddress"]["region"]
        zip_code = poi["postalAddress"]["code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["postalAddress"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["contacts"]["phone"]
        latitude = poi["geoLocation"]["lat"]
        longitude = poi["geoLocation"]["lng"]
        hours_of_operation = "<MISSING>"

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
