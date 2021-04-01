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

    DOMAIN = "bakersdrivethru.com"
    start_url = "https://www.bakersdrivethru.com/?sm-xml-search=1&lat=34.0738059&lng=-117.3132806&radius=0&namequery=34.0739016%2C%20-117.31365470000003&query_type=all&limit=0&sm_category&sm_tag&sm_day&sm_time&locname&address&city&state&zip&pid=5"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = "https://www.bakersdrivethru.com/locations/"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        city = poi.get("city")
        city = city if city else "<MISSING>"
        state = poi["state"]
        zip_code = poi["zip"]
        country_code = poi["country"]
        store_number = poi["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
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
