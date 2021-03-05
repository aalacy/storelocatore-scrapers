import re
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://storerocket.global.ssl.fastly.net/api/user/VyJzm2D46M/locations?radius=50&units=miles"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["results"]["locations"]:
        store_url = (
            f'https://www.usaveitpharmacy.com/26-locations/?location={poi["slug"]}'
        )
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address_line_1"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["state"]
        state = state if state else "<MISSING>"
        zip_code = poi["postcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"].split(", ")[-1]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hoo = []
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for day in days:
            hours = poi[day]
            hoo.append(f"{day} {hours}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

        item = [
            domain,
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
