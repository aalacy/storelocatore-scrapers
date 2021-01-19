import csv
import json
from w3lib.html import remove_tags

from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w") as output_file:
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

    DOMAIN = "esso.co.uk"
    start_url = "https://www.esso.co.uk/en-GB/api/locator/Locations?Latitude1=48.356492210436045&Latitude2=60.94128404594158&Longitude1=-22.645048209150662&Longitude2=16.246553353349338&DataSource=RetailGasStations&Country=GB&Customsort=False"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = (
            "https://www.esso.co.uk/en-gb/find-station/{}--essobranchend-{}".format(
                poi["City"].lower(), poi["LocationID"]
            )
        )
        location_name = poi["LocationName"]
        street_address = poi["AddressLine1"]
        if poi["AddressLine2"]:
            street_address += " " + poi["AddressLine2"]
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["StateProvince"]
        state = state if state else "<MISSING>"
        zip_code = poi["PostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Country"]
        store_number = poi["LocationID"]
        phone = poi["Telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["EntityType"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = remove_tags(poi["WeeklyOperatingHours"])

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
