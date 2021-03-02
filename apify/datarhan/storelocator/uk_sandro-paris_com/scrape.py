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

    DOMAIN = "sandro-paris.com"

    start_url = "https://uk.sandro-paris.com/on/demandware.store/Sites-Sandro-UK-Site/en_GB/Stores-GetStores"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://uk.sandro-paris.com/en/stores"
        location_name = poi["properties"]["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["properties"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["properties"]["city"]
        city = city if city else "<MISSING>"
        state = poi["properties"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["properties"]["zip"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["properties"]["countryCode"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code != "us":
            continue
        store_number = poi["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["properties"]["phone"]
        phone = phone if phone and phone != "0" else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        if poi["properties"].get("storeHours"):
            hoo = poi["properties"]["storeHours"].replace("|", "")
        hours_of_operation = hoo if hoo else "<MISSING>"

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
