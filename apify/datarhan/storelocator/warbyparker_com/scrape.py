import re
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

    DOMAIN = "warbyparker.com"
    start_url = "https://www.warbyparker.com/retail"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "WarbyParker")]/text()')[0]
    data = re.findall("WarbyParker = (.+);", data)[0]
    data = json.loads(data)

    for poi in data["api"]["prefetched"]["/api/v2/retail/locations"]["locations"]:
        store_url = "https://www.warbyparker.com/retail/{}/{}".format(
            poi["city_slug"], poi["location_slug"]
        )
        location_name = poi["name"]
        street_address = poi["address"]["street_address"]
        city = poi["address"]["locality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["region_code"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postal_code"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["country_code"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["cms_content"]["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["cms_content"]["map_details"]["latitude"]
        longitude = poi["cms_content"]["map_details"]["longitude"]
        hours_of_operation = []
        for day, hours in poi["schedules"][0]["hours"].items():
            if not hours.get("open"):
                hours_of_operation.append(f"{day} closed")
            else:
                opens = hours["open"]
                closes = hours["close"]
                hours_of_operation.append(f"{day} {opens} - {closes}")
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
