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

    DOMAIN = "gmoc.com"
    start_url = "https://www.gmoc.com/wp-json/gmoc/v1/locations?MinLong=-118.428789125&MaxLong=-117.549882875&MinLat=33.612150836176625&MaxLat=33.77440057819261"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["stations"]:
        store_url = "<MISSING>"
        location_name = poi["store_name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        city = poi["city"]
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["ID"]
        phone = poi.get("phone_number")
        phone = phone if phone else "<MISSING>"
        location_type = poi["brand"]["slug"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hoo = []
        for key, value in poi.items():
            if "_day" in key:
                hoo.append(f"{value} 24-Hours")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
