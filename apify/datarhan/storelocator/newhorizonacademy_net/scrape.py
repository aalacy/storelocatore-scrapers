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

    DOMAIN = "newhorizonacademy.net"
    start_url = "https://www.newhorizonacademy.net/wp-admin/admin-ajax.php?action=nha_get_locations"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["results"]:
        store_url = poi["post_url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["post_title"]
        location_name = (
            location_name.replace("&#8211;", "-").replace("&#8217;", "'")
            if location_name
            else "<MISSING>"
        )
        street_address = poi["address_line_1"]
        if poi["address_line_2"]:
            street_address += " " + poi["address_line_2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["zip_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["location"]["address"].split(", ")[-1]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["location"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["location"]["lng"]
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
