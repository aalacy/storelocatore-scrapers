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

    DOMAIN = "jollyes.co.uk"
    start_url = "https://www.jollyes.co.uk/locator/"

    response = session.get(start_url)
    data = re.findall("stores = (.+?);", response.text)[0]
    data = json.loads(data)

    for poi in data["items"]:
        store_url = poi["store_popup_url"]
        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]
        if poi["address1"]:
            if poi["address1"] not in street_address:
                street_address += ", " + poi["address1"]
        if poi["address2"]:
            if poi["address2"] not in street_address:
                street_address += ", " + poi["address2"]
        city = poi["city"]
        city = city if city else "<MISSING>"
        state = poi["county"]
        state = state if state else "<MISSING>"
        zip_code = poi["zipcode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["country_id"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["shop_id"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["phone"]
        phone = phone if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = poi["lat"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["long"]
        longitude = longitude if longitude else "<MISSING>"

        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        hours_of_operation = loc_dom.xpath(
            '//div[@class="addr3"]//div[@class="arrange-margin"]/p//text()'
        )[:10]
        hours_of_operation = (
            ", ".join(hours_of_operation).split(", CHRISTMAS")[0].replace(": ,", ":")
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
