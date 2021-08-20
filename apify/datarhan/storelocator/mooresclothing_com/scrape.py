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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://stores.mooresclothing.com/index.html"
    domain = "mooresclothing.com"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = []
    regions = dom.xpath('//div[@class="sb-module sb-directorystateslist"]//a/@href')
    for url in regions[1:]:
        response = session.get(urljoin(start_url, url))
        dom = etree.HTML(response.text)
        cities = dom.xpath('//div[@class="sb-module sb-directory"]//a/@href')
        for url in cities[1:]:
            response = session.get(urljoin(start_url, url))
            dom = etree.HTML(response.text)
            all_locations += dom.xpath(
                '//div[@class="sb-module sb-directory"]//a/@href'
            )

    for url in list(set(all_locations)):
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "streetAddress")]/text()')
        if not poi:
            continue
        poi = json.loads(poi[0])

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["address"]["addressCountry"]["name"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = (
            loc_dom.xpath('//p[contains(text(), "Store ID")]/text()')[0]
            .split("ID")[-1]
            .strip()
        )
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi.get("geo"):
            latitude = poi["geo"]["latitude"]
            longitude = poi["geo"]["longitude"]
        hoo = poi["openingHours"]
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo[2:]) if hoo else "<MISSING>"

        item = [
            domain,
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
