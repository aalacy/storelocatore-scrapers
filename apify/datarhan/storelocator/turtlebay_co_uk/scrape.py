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

    DOMAIN = "turtlebay.co.uk"
    start_url = "https://www.turtlebay.co.uk/api/locations/items.json"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data["data"]:
        store_url = poi["url"]
        location_name = poi["title"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["line1"]
        if poi["address"]["line2"]:
            street_address += " " + poi["address"]["line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"]
        city = city if city and "n/a" not in city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["address"]["postcode"]
        zip_code = zip_code if zip_code and "n/a" not in zip_code else "<MISSING>"
        country_code = "UK"
        store_number = poi["id"]
        phone = poi["contact"]
        phone = (
            phone[0]["phone"]
            if phone and "n/a" not in phone[0]["phone"]
            else "<MISSING>"
        )
        location_type = "<MISSING>"
        if "t open right now" in zip_code:
            location_type = "temporary closed"
            zip_code = "<MISSING>"
        latitude = poi["address"]["latitude"]
        latitude = latitude if latitude and "n/a" not in latitude else "<MISSING>"
        longitude = poi["address"]["longitude"]
        longitude = longitude if longitude and "n/a" not in longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"
        if poi["openingHours"]:
            hours_of_operation = " ".join(
                [elem["label"] for elem in poi["openingHours"]]
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
