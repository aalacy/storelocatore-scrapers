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

    DOMAIN = "kegsteakhouse.com"
    start_url = "https://kegsteakhouse.com/en/location/list"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://kegsteakhouse.com" + poi["drupal"]["url"]
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["singleplatform"]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["singleplatform"]["location"]["address1"]
        if poi["singleplatform"]["location"]["address2"]:
            street_address += ", " + poi["singleplatform"]["location"]["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["singleplatform"]["location"]["city"]
        city = city if city else "<MISSING>"
        state = poi["singleplatform"]["location"]["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["singleplatform"]["location"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["singleplatform"]["location"]["country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["singleplatform"]["location_nid"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["singleplatform"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["singleplatform"]["business_type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["singleplatform"]["location"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["singleplatform"]["location"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if not type(poi["singleplatform"]["hours"]) == list:
            for day, hours in poi["singleplatform"]["hours"].items():
                opens = hours[0]["opening"]
                closes = hours[0]["closing"]
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
        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
