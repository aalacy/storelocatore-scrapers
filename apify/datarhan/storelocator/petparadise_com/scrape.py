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

    DOMAIN = "petparadise.com"
    start_url = "https://www.petparadise.com/files/4859/widget856515.js?callback=widget856515DataCallback&_=1611159764874"
    response = session.get(start_url)
    data = response.text.split("DataCallback(")[-1][:-2]
    data = json.loads(data)

    for poi in data["PropertyorInterestPoint"]:
        store_url = poi["interestpointMoreInfoLink"]
        location_name = poi["interestpointpropertyname"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["interestpointpropertyaddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["interestpointCity"]
        city = city if city else "<MISSING>"
        state = poi["interestpointState"]
        state = state if state else "<MISSING>"
        zip_code = poi["interestpointPostalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["interestpointPhoneNumber"]
        phone = phone if phone else "<MISSING>"
        if phone == "TBD":
            phone = "<MISSING>"
        location_type = poi["interestpointVetStatus"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["interestpointinterestlatitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["interestpointinterestlongitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = etree.HTML(poi["interestpointHours"])
        hours_of_operation = hours_of_operation.xpath("//text()")
        hours_of_operation = (
            " ".join(hours_of_operation).replace("Location Hours ", "")
            if hours_of_operation
            else "<MISSING>"
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
