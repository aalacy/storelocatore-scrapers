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

    DOMAIN = "twinpeaksrestaurant.com"
    start_url = "https://twinpeaksrestaurant.com/api/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = poi["link"]
        location_name = poi["acf"]["city"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["acf"]["address"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["acf"]["city"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        if poi["acf"]["state"]:
            state = poi["acf"]["state"]["value"]
        state = state if state else "<MISSING>"
        zip_code = poi["acf"]["postal"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["acf"]["country"]["value"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code != "US":
            continue
        store_number = poi["id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["acf"]["phone_number"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if poi["acf"]["market"]:
            location_type = poi["acf"]["market"]["post_type"]
        if poi["acf"]["status"] == "coming_soon":
            location_type = "coming soon"
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["acf"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["acf"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if poi["acf"]["hours"]:
            for elem in poi["acf"]["hours"]:
                day = elem["day"]["label"]
                opens = elem["opens"]
                closes = elem["closes"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
