import csv
import json
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
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = "bentleymotors.com"
    start_url = "https://www.bentleymotors.com/content/brandmaster/global/bentleymotors/en/apps/dealer-locator/jcr:content.api.6cac2a5a11b46ea2d9c31ae3f98bfeb0.json"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["dealers"]:
        poi_response = session.get(urljoin(start_url, poi["url"]))
        data = json.loads(poi_response.text)

        location_name = data["dealerName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = data["addresses"][0]["street"]
        street_address = street_address if street_address else "<MISSING>"
        city = data["addresses"][0]["city"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = data["addresses"][0].get("postcode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = data["addresses"][0]["country"]
        country_code = country_code if country_code else "<MISSING>"
        if country_code not in ["UK", "United Kingdom"]:
            continue
        store_number = data["id"]
        phone = data["addresses"][0]["departments"][0].get("phone")
        phone = phone if phone else "<MISSING>"
        store_url = data["addresses"][0]["departments"][0].get("website")
        store_url = store_url if store_url else "<MISSING>"
        location_type = "<MISSING>"
        latitude = data["addresses"][0]["wgs84"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = data["addresses"][0]["wgs84"]["lng"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        for elem in data["addresses"][0]["departments"][0]["openingHours"]:
            if elem["periods"]:
                day = elem["day"]
                if elem["closed"] is False:
                    opens = elem["periods"][0]["open"]
                    closes = elem["periods"][0]["close"]
                    hoo.append(f"{day} {opens} - {closes}")
                else:
                    hoo.append(f"{day} closed")

        hours_of_operation = ", ".join(hoo) if hoo else "<MISSING>"

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

        if location_name not in scraped_items:
            scraped_items.append(location_name)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
