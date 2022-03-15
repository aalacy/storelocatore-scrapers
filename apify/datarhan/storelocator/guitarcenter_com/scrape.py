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

    DOMAIN = "guitarcenter.com"
    start_url = "https://stores.guitarcenter.com/browse/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations_urls = []
    directories_urls = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')

    for url in directories_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        urls = dom.xpath('//div[@class="map-list-item is-single"]/a/@href')
        for url in urls:
            response = session.get(url)
            dom = etree.HTML(response.text)
            all_locations_urls += dom.xpath('//a[@class="more-details ga-link"]/@href')

    for store_url in all_locations_urls:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')[0]
        poi = json.loads(poi)

        location_name = loc_dom.xpath(
            '//div[@class="row headerContainer indy-main-wrapper"]/div/text()'
        )[0]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi[0]["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi[0]["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi[0]["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi[0]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi[0]["address"]["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi[0]["@type"]
        latitude = poi[0]["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi[0]["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hours_of_operation = poi[0]["openingHours"]

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
