import re
import csv
import json
from lxml import etree
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

    DOMAIN = "joules.com"
    start_url = "https://www.joules.com/store-finder"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[contains(text(), "storeResults")]/text()')[0]
    data = re.findall("storeResults = (.+);", data.replace("\n", ""))
    data = json.loads(data[0])

    for poi in data.values():
        store_url = urljoin(start_url, poi["url"])
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        data = loc_dom.xpath('//div[@class="row store-details"]/script/text()')
        data = json.loads(data[0])

        location_name = data["name"]
        street_address = data["address"]["streetAddress"]
        city = data["address"]["addressRegion"]
        city = city if city else "<MISSING>"
        state = "<MISSING>"
        zip_code = data["address"].get("postalCode")
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = poi["storeId"]
        store_number = store_number if store_number else "<MISSING>"
        phone = data.get("telephone")
        phone = phone if phone else "<MISSING>"
        location_type = data["@type"]
        latitude = poi["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        if data.get("openingHoursSpecification"):
            for elem in data["openingHoursSpecification"]:
                day = elem["dayOfWeek"].split("/")[-1]
                opens = elem["opens"]
                closes = elem["closes"]
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
