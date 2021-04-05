import csv
import json
from w3lib.html import remove_tags

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

    DOMAIN = "oceanstatejoblot.com"
    start_url = "https://www.oceanstatejoblot.com/ccstoreui/v1/locations"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["items"]:
        store_url = "https://www.oceanstatejoblot.com/store-details?storeid={}".format(
            poi["locationId"]
        )
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateAddress"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["locationId"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = poi.get("hours")
        hours_of_operation = (
            remove_tags(hours_of_operation).replace("&nbsp;", " ").split("/20")[-1]
            if hours_of_operation
            else "<MISSING>"
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
