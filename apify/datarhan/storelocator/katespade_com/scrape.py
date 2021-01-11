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
    scraped_items = []

    DOMAIN = "katespade.com"
    start_url = "https://katespade.brickworksoftware.com/en_US/api/v3/stores.json"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["stores"]:
        store_url = "https://www.katespade.com/stores/s/" + poi["slug"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address_1"]
        if poi["address_2"]:
            street_address += ", " + poi["address_2"]
        if poi["address_3"]:
            street_address += ", " + poi["address_3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country_code"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = ""
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone_number"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["regular_hours"]:
            day = elem["display_day"]
            opens = elem["display_start_time"]
            closes = elem["display_end_time"]
            hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
        if street_address not in scraped_items:
            scraped_items.append(street_address)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
