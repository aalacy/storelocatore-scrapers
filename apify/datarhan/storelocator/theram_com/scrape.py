import csv
import json

from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address_usa


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

    session = SgRequests()

    DOMAIN = "theram.com"
    start_url = "https://api2.storepoint.co/v1/15b0d715039ef2/locations?lat=39.4667&long=-0.7167&radius=7000"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["results"]["locations"]:
        store_url = "<MISSING>"
        location_name = poi["name"]
        location_name = location_name.split("> ")[-1] if location_name else "<MISSING>"
        addr = parse_address_usa(poi["streetaddress"])
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_2 + " " + addr.street_address_1
        street_address = street_address if street_address else "<MISSING>"
        city = addr.city
        city = city if city else "<MISSING>"
        state = addr.state
        state = state if state else "<MISSING>"
        zip_code = addr.postcode
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = addr.country
        store_number = poi["id"]
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["loc_lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["loc_long"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for day in days:
            hoo.append(f"{day} {poi[day]}")
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
