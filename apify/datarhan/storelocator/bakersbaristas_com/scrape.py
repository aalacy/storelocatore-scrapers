import csv
import json

from sgrequests import SgRequests

MISSING = "<MISSING>"


def get(location, key):
    return location.get(key, MISSING) or MISSING


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

    DOMAIN = "bakersbaristas.com"
    start_url = "https://www.bakersbaristas.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=65455a331a&load_all=1&layout=1"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "<MISSING>"
        location_name = get(poi, "title")
        street_address = get(poi, "street")
        city = get(poi, "city")
        state = get(poi, "state")
        zip_code = get(poi, "postal_code")
        country_code = get(poi, "country")
        if country_code == "Ireland":
            continue
        store_number = get(poi, "id")
        phone = get(poi, "phone")
        location_type = "<MISSING>"
        latitude = get(poi, "lat")
        longitude = get(poi, "lng")
        hoo = []
        for day, hours in json.loads(poi["open_hours"]).items():
            hoo.append(f"{day} {hours[0]}")
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

        if location_name not in scraped_items:
            scraped_items.append(location_name)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
