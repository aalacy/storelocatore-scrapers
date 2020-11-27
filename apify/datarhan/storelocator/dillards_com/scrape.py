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

    DOMAIN = "dillards.com"
    start_url = "https://www.dillards.com/stores"

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36",
    }
    response = session.post(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_poi_urls = dom.xpath('//div[@id="storeListing"]//a[@class="underline"]/@href')
    for url in all_poi_urls:
        store_url = "https://www.dillards.com/" + url
        store_response = session.get(store_url)
        store_dom = etree.HTML(store_response.text)
        store_data = store_dom.xpath('//div[@id="storeDetails"]/script/text()')[0]
        store_data = json.loads(store_data)

        location_name = store_data["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = store_data["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = store_data["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = store_data["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = store_data["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = ""
        country_code = country_code if country_code else "<MISSING>"
        store_number = store_data["url"].split("/")[-1]
        store_number = store_number if store_number else "<MISSING>"
        phone = store_data["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = store_data["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = ""
        latitude = latitude if latitude else "<MISSING>"
        longitude = ""
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = []
        for elem in store_data["openingHoursSpecification"]:
            day = elem["dayOfWeek"]["name"]
            opens = elem["opens"]
            closes = elem["closes"]
            hours_of_operation.append("{} {} - {}".format(day, opens, closes))
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
