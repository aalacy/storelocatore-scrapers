import re
import csv
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
    session = SgRequests().requests_retry_session(retries=2, backoff_factor=0.3)

    items = []

    DOMAIN = "flynnstire.com"
    start_url = "https://www.flynnstire.com/stores/"

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[contains(text(), "View Details")]/@href')
    for store_url in list(set(all_locations)):
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//div[@class="inner_content"]//span/h2/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@class="retailer-name"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath(
            '//span[@class="retailer-name"]/following-sibling::span//text()'
        )[0].split(", ")[0]
        state = loc_dom.xpath(
            '//span[@class="retailer-name"]/following-sibling::span//text()'
        )[0].split(", ")[-1]
        zip_code = "<MISSING>"
        geo = re.findall(r"latLng:\[(.+?)\],", loc_response.text)[0].split(",")
        latitude = geo[0]
        longitude = geo[1]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//span[@class="retailer-name"]/following-sibling::span//text()'
        )[-1]
        location_type = "<MISSING>"
        hoo = loc_dom.xpath('//p[@class="retailer-hours"]//text()')
        hoo = [elem.strip() for elem in hoo if elem.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
