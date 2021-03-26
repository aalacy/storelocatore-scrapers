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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    start_url = "https://www.sonesta.com/sonestahotel"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="layout-listing__title-linked"]/@href')
    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[@data-react-helmet="true"]/text()')[0]
        poi = json.loads(poi)

        location_name = poi["@graph"][0]["name"]
        location_name = location_name if location_name else "<MISSING>"
        street_address = poi["@graph"][0]["address"]["streetAddress"]
        street_address = street_address if street_address else "<MISSING>"
        city = poi["@graph"][0]["address"]["addressLocality"]
        city = city if city else "<MISSING>"
        state = poi["@graph"][0]["address"]["addressRegion"]
        state = state if state else "<MISSING>"
        zip_code = poi["@graph"][0]["address"]["postalCode"]
        zip_code = zip_code if zip_code else "<MISSING>"
        country_code = poi["@graph"][0]["address"]["addressCountry"]
        country_code = country_code if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["@graph"][0].get("telephone")
        phone = phone if phone else "<MISSING>"
        location_type = poi["@graph"][0].get("@type")
        location_type = location_type if location_type else "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if poi["@graph"][0].get("geo"):
            latitude = poi["@graph"][0]["geo"]["latitude"]
            longitude = poi["@graph"][0]["geo"]["longitude"]
        hours_of_operation = "<MISSING>"

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
