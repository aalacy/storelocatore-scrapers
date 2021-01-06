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
    scraped_items = []

    DOMAIN = "olympiasports.net"
    start_url = "https://www.olympiasports.net/on/demandware.store/Sites-OlympiaSports-Site/en_US/Stores-FindStores?showMap=false&radius=50000&lat=34.1571232&long=-118.4913086"
    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["stores"]:
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address1"]
        if poi["address2"]:
            street_address += ", " + poi["address2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["stateCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["countryCode"]
        store_number = poi["ID"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        longitude = poi["longitude"]
        hours_of_operation = "<MISSING>"

        if len(city) == 2:
            state = city
            city = poi["stateCode"]

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
