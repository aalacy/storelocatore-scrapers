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

    DOMAIN = "lamborghini.com"
    start_url = "https://www.lamborghini.com/dealers/get.json/en"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["item"]:
        if poi["address"]["country"] not in [
            "United States",
            "Canada",
            "United Kingdom",
        ]:
            continue
        store_url = "<MISSING>"
        location_name = poi["description"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["city"].split(",")[0]
        state = "<MISSING>"
        zip_code = poi["address"]["zip"]
        country_code = poi["address"]["countryCode"]
        if country_code == "US":
            zip_code = zip_code.split()[-1]
            state = poi["address"]["zip"].split()[0]
        store_number = poi["nid"]
        phone = poi.get("contact", {}).get("phone")
        phone = phone if phone else "<MISSING>"
        location_type = poi["type"]["label"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["coordinates"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["coordinates"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = "<MISSING>"

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
