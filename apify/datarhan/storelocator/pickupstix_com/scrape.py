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

    DOMAIN = "pickupstix.com"
    start_url = "https://www.pickupstix.com/locations"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36"
    }

    response = session.post(start_url, headers=headers)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//div[@class="all-locations"]//div/a[h4]/@href')

    for store_url in all_locations:
        store_url = urljoin(start_url, store_url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath(
            '//script[@type="application/ld+json" and contains(text(), "geo")]/text()'
        )[0]
        poi = json.loads(poi.replace("\n", "").replace("\t", ""))

        location_name = poi["name"]
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"].strip()
        state = poi["address"]["addressRegion"].strip()
        zip_code = poi["address"]["postalCode"]
        phone = poi["telephone"]
        country_code = poi["address"]["addressCountry"]
        store_number = "<MISSING>"
        location_type = poi["@type"]
        latitude = poi["geo"]["latitude"]
        longitude = poi["geo"]["longitude"]
        hours_of_operation = " ".join(poi["openingHours"].split())

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
