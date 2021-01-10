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

    DOMAIN = "safeguardit.com"
    start_urls = [
        "https://www.safeguardit.com/florida-storage",
        "https://www.safeguardit.com/illinois-storage",
        "https://www.safeguardit.com/louisiana-storage",
        "https://www.safeguardit.com/new-jersey-storage",
        "https://www.safeguardit.com/new-york-storage",
        "https://www.safeguardit.com/pennsylvania-storage",
    ]

    all_locations = []
    for url in start_urls:
        response = session.get(url)
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//div[@class="storeAddress"]/h4/a/@href')

    for url in list(set(all_locations)):
        store_url = urljoin(start_urls[0], url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@type="application/ld+json"]/text()')[1]
        poi = json.loads(
            poi.replace("\r", "").replace("\n", "").replace('" Bob "', " Bob ")
        )

        location_name = poi["name"]
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = poi["address"]["addressCountry"]
        store_number = "<MISSING>"
        phone = poi["telephone"]
        phone = phone if phone else "<MISSING>"
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hours_of_operation = poi["openingHours"].replace("&nbsp;", "")

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
