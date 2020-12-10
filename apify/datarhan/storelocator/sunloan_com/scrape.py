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

    DOMAIN = "sunloan.com"

    start_url = "https://www.sunloan.com/wp-json/sunloan/v1/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["url"]
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["full_address"]["address"]
        if poi["full_address"]["address2"]:
            street_address += ", " + poi["full_address"]["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["full_address"]["city"]
        city = city if city else "<MISSING>"
        state = poi["full_address"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["full_address"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["full_address"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["full_address"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["full_address"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for day, hours in poi["hours"].items():
            if hours:
                opens = " - ".join(hours[0].split(","))
            else:
                opens = "closed"
            hours_of_operation.append("{} {}".format(day, opens))
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
