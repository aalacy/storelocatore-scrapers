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
    session = SgRequests().requests_retry_session(retries=3, backoff_factor=0.3)

    items = []

    DOMAIN = "storquest.com"
    start_url = "https://www.storquest.com/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//td[@class="directory-location-name p-name"]/a/@href')

    for store_url in all_locations:
        loc_response = session.get(store_url, headers=headers)
        loc_dom = etree.HTML(loc_response.text)
        store_data = loc_dom.xpath('//script[@class="structured-data-widget"]/text()')
        store_data = json.loads(store_data[0].replace("\n", "").replace("\r", ""))

        location_name = store_data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = store_data["address"]["streetAddress"]
        city = store_data["address"]["addressLocality"]
        state = store_data["address"]["addressRegion"]
        zip_code = store_data["address"]["postalCode"]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = store_data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = store_data["@type"]
        latitude = store_data["geo"]["latitude"]
        longitude = store_data["geo"]["longitude"]
        hours_of_operation = []
        for elem in store_data["openingHoursSpecification"]:
            day = elem["dayOfWeek"][0]
            opens = elem["opens"]
            closes = elem["closes"]
            hours_of_operation.append(f"{day} {opens} {closes}")
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
