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

    DOMAIN = "speedeeoil.com"

    start_url = "https://www.speedeeoil.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=ebbc26379a&load_all=1&layout=1"
    response = session.get(start_url)
    data = json.loads(response.text)
    for point in data:
        store_url = point["website"]
        location_name = point["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = point["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = point["city"]
        city = city if city else "<MISSING>"
        state = point["state"]
        state = state if state else "<MISSING>"
        zip_code = point["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = point["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = point["id"]
        phone = point["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        location_type = location_type if location_type else "<MISSING>"
        latitude = point["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = point["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation_raw = json.loads(point["open_hours"])
        hours_of_operation = []
        for day, hours in hours_of_operation_raw.items():
            hours = hours[0]
            hours = "<closed>" if len(hours.strip()) == 1 else hours
            hours_of_operation.append("{} - {}".format(day, hours))
        hours_of_operation = ", ".join(hours_of_operation)

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
