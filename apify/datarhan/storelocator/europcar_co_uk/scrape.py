import csv
import json
from urllib.parse import urljoin

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

    DOMAIN = "europcar.co.uk"
    start_url = "https://www.europcar.co.uk/en_GB/contents/worldwide/WESTEUR/GB/car.stations.json"

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data:
        store_url = urljoin(start_url, poi["url"])
        location_name = poi["name"]
        street_address = " ".join(poi["address"]["streetLines"])
        city = poi["address"]["city"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = poi["address"]["postCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country"]
        if country_code != "United Kingdom":
            continue
        store_number = "<MISSING>"
        phone = poi["phone"]["phoneNumber"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
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
