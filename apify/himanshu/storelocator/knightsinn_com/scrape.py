import re
import csv
from urllib.parse import urljoin

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
    items = []

    start_url = "https://www.redlion.com/locations"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    session = SgRequests()
    data = session.get(
        "https://www.redlion.com/page-data/locations/page-data.json"
    ).json()
    static_hashes = data["staticQueryHashes"]

    for hash in static_hashes:
        response = session.get(
            f"https://www.redlion.com/page-data/sq/d/{hash}.json"
        ).json()
        data = response["data"]
        all_hotels = data.get("allHotel")
        if not all_hotels:
            continue

        all_locations = all_hotels["nodes"]

    for poi in all_locations:
        store_url = urljoin(start_url, poi["path"]["alias"])
        poi = session.get(
            f'https://www.redlion.com/page-data{poi["path"]["alias"]}/page-data.json'
        ).json()
        poi = poi["result"]["data"]["hotel"]

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["address_line1"]
        if poi["address"].get("address_line2"):
            street_address += " " + poi["address"]["address_line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["locality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["administrative_area"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country_code"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat_lon"]["lat"]
        longitude = poi["lat_lon"]["lon"]
        hours_of_operation = "<MISSING>"

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
