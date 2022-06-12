import csv
import json
from lxml import etree

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

    DOMAIN = "onelifefitness.com"
    start_url = (
        "https://api.hubapi.com/hubdb/api/v2/tables/673686/rows?portalId=2094550"
    )

    response = session.get(start_url)
    data = json.loads(response.text)

    for poi in data["objects"]:
        store_url = "https://www.onelifefitness.com/gyms/" + poi["path"]
        location_name = poi["name"]
        street_address = poi["values"]["11"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["values"]["10"]
        city = city if city else "<MISSING>"
        state = poi["values"]["9"]
        state = state if state else "<MISSING>"
        zip_code = poi["values"]["12"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["values"]["14"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        if "Coming Soon" in phone:
            phone = "<MISSING>"
            location_type = "coming soon"
        latitude = poi["values"]["7"]["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["values"]["7"]["long"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = ""
        if poi["values"].get("22"):
            hours_of_operation = etree.HTML(poi["values"]["22"])
            hours_of_operation = hours_of_operation.xpath("//text()")
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
        hours_of_operation = (
            " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
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
