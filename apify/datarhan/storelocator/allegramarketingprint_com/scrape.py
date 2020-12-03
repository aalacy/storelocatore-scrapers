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
    session = SgRequests().requests_retry_session(retries=0, backoff_factor=0.3)

    items = []

    DOMAIN = "allegramarketingprint.com"
    start_url = "https://www.allegramarketingprint.com/frontend/locationsMap.js"

    response = session.get(start_url)
    data = re.findall("franchiseeLocations = (.+);", response.text)
    data = json.loads(data[0])

    for poi in data:
        store_url = poi["MicroSiteUrl"].replace("http:", "https:")
        store_url = store_url if store_url else "<MISSING>"
        location_name = poi["LocationName"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["Line1"]
        if poi["Line2"]:
            street_address += ", " + poi["Line2"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["City"]
        city = city if city else "<MISSING>"
        state = poi["State"]
        state = state if state else "<MISSING>"
        zip_code = poi["Postal"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["Country"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = poi["LocationNumber"]
        store_number = store_number if store_number else "<MISSING>"
        phone = poi["Phone"]
        phone = phone if phone else "<MISSING>"
        location_type = ""
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["Latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["Longitude"]
        longitude = longitude if longitude else "<MISSING>"

        try:
            store_response = session.get(store_url)
            store_dom = etree.HTML(store_response.text)
            hours_of_operation = store_dom.xpath(
                '//div[@class="oprationalHours"]//text()'
            )
            hours_of_operation = [
                elem.strip() for elem in hours_of_operation if elem.strip()
            ]
            hours_of_operation = (
                " ".join(hours_of_operation) if hours_of_operation else "<MISSING>"
            )
        except:
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
