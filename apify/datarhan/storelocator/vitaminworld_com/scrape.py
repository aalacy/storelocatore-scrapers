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
    scraped_items = []

    DOMAIN = "vitaminworld.com"
    start_url = "https://www.vitaminworld.com/on/demandware.store/Sites-vitaminworld_us-Site/default/Stores-GetNearestStores?latitude=37.0910199&longitude=+-95.71094269999999&postalCode=67301&countryCode=US&distanceUnit=mi&maxdistance=50000"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["stores"]:
        store_url = "<MISSING>"
        location_name = poi["name"]
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        city = poi["city"]
        state = poi["stateCode"]
        zip_code = poi["postalCode"]
        country_code = "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = poi["storeHours"]
        hours_of_operation = (
            remove_tags(hours_of_operation).strip()
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
        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
