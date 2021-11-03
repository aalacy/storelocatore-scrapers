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

    DOMAIN = "intermixonline.com"
    start_url = "https://www.intermixonline.com/storeresults?dwfrm_storelocator_distanceUnit=mi&dwfrm_storelocator_findall=Search"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//a[@title="View Store Details"]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        poi = json.loads(poi)

        location_name = poi["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["addressCountry"]
        store_number = store_url.split("=")[-1]
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        location_type = location_type if location_type else "<MISSING>"
        latitude = poi["geo"]["latitude"]
        latitude = latitude if latitude else "<MISSING>"
        longitude = poi["geo"]["longitude"]
        longitude = longitude if longitude else "<MISSING>"
        hoo = []
        if poi.get("openingHoursSpecification"):
            for elem in poi["openingHoursSpecification"]:
                for day in elem["dayOfWeek"]:
                    hoo.append(f'{day} {elem["opens"]} - {elem["closes"]}')
        if not hoo:
            hoo = loc_dom.xpath(
                '//div[@class="details-header"]/following-sibling::div//li//span/text()'
            )
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        if hours_of_operation == "<MISSING>":
            location_type = "closed"

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
