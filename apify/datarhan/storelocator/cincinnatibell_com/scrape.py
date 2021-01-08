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

    DOMAIN = "cincinnatibell.com"
    start_url = "https://www.cincinnatibell.com/api/locations/getlocations"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "<MISSING>"
        location_name = poi["name"].strip()
        street_address = poi["address"]["street"]
        street_address = street_address.strip() if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city.strip() if city else "<MISSING>"
        state = poi["address"]["state"]
        state = state.strip() if state else "<MISSING>"
        zip_code = poi["address"]["zip"]
        zip_code = zip_code.strip() if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]
        latitude = poi["geoloc"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geoloc"]["lon"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi["hours"]
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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
