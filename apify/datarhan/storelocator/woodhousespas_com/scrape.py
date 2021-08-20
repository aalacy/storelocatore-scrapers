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

    DOMAIN = "woodhousespas.com"
    start_url = "https://api2.storepoint.co/v1/1605a745e2ae6a/locations?lat=40.75&long=-73.99&radius=10000"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["results"]["locations"]:
        store_url = "https://" + poi["website"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        raw_address = poi["streetaddress"].split(",")
        if len(raw_address) == 5:
            raw_address = raw_address[:2] + raw_address[3:]
        if len(raw_address) == 4:
            raw_address = raw_address[:-1]
        street_address = raw_address[0]
        city = raw_address[1]
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["id"]
        latitude = poi["loc_lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["loc_long"]
        longitude = longitude if longitude else "<MISSING>"
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
