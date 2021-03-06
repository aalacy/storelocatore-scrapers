import csv
import json

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_intl


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

    DOMAIN = "sandro-paris.com"
    start_url = "https://us.sandro-paris.com/on/demandware.store/Sites-Sandro-US-Site/en_US/Stores-GetStores"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        country_code = poi["properties"]["countryCode"]
        if country_code != "us":
            continue
        store_url = "https://us.sandro-paris.com/en/stores"
        location_name = poi["properties"]["title"]
        location_name = location_name if location_name else "<MISSING>"
        city = poi["properties"]["city"]
        addr = parse_address_intl(poi["properties"]["address"])
        street_address = addr.street_address_1
        zip_code = poi["properties"]["zip"]
        state = poi["properties"]["state"]
        if not state:
            if len(zip_code) > 5:
                state = zip_code[:2]
                zip_code = zip_code[2:]
        state = state if state else "<MISSING>"
        store_number = poi["id"]
        location_type = "<MISSING>"
        if "<" in location_name:
            location_name = location_name.split("<")[0]
            location_type = "temporarily closed"
        phone = poi["properties"]["phone"]
        phone = phone if phone and phone != "0" else "<MISSING>"
        latitude = poi["lat"]
        longitude = poi["lng"]
        hours_of_operation = poi["properties"]["storeHours"].replace("|", "")

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
