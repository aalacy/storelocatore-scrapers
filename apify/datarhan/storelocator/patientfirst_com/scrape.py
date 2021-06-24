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

    DOMAIN = "patientfirst.com"
    start_url = "https://www.patientfirst.com/locations-sitemap.xml"

    all_urls = []
    response = session.get(start_url)
    root = etree.fromstring(response.content)
    for sitemap in root:
        children = sitemap.getchildren()
        all_urls.append(children[0].text)

    for store_url in all_urls:
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)
        poi = loc_dom.xpath('//script[contains(text(), "alternateName")]/text()')[0]
        poi = json.loads(poi.replace("\r\n", ""))

        location_name = poi["alternateName"]
        street_address = poi["address"]["streetAddress"]
        city = poi["address"]["addressLocality"]
        state = poi["address"]["addressRegion"]
        zip_code = poi["address"]["postalCode"]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = poi["telephone"]
        location_type = poi["@type"]
        geo = loc_dom.xpath('//img[@id="mapimage"]/@src')[0].split("=")[-1].split(",")
        latitude = geo[0]
        longitude = geo[1]
        hours_of_operation = poi["openingHours"]
        # hours_of_operation = hours_of_operation.replace(
        #     "Regular and after hours medical care, ", ""
        # )
        # hours_of_operation = hours_of_operation.replace(
        #     ", including weekends and holidays", ""
        # )

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
