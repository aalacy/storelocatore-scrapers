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

    DOMAIN = "freshii.com"

    start_url = "https://orders.freshii.com/api/locations?northeastLat=69.44728343853946&northeastLong=42.93119000000001&southwestLat=-6.562715243529688&southwestLong=139.25931500000002&lang=en&device-id=16062951130708532736&tkn=0EAF469F44C453DF34A8E398F8E80E92F7F1DCABD7A1776D9F3C5A90010ACF23"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)

    for poi in data:
        store_url = "<MISSING>"
        location_name = poi["Name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Address"]["AddressLine1"]
        if poi["Address"]["AddressLine2"]:
            street_address += " " + poi["Address"]["AddressLine2"]
        if poi["Address"]["AddressLine3"]:
            street_address += " " + poi["Address"]["AddressLine3"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["Address"]["City"]
        city = city if city else "<MISSING>"
        state = poi["Address"]["StateProvinceCode"]
        state = state if state else "<MISSING>"
        zip_code = poi["Address"]["PostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Address"]["CountryCode"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["Id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Address"]["PhoneNum"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["GeoCoordinate"]["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["GeoCoordinate"]["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in poi["AvailabilitySchedules"]:
            hours_of_operation.append(
                "{} {} - {}".format(elem["Day"], elem["StartTime"], elem["EndTime"])
            )
        hours_of_operation = (
            ", ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
