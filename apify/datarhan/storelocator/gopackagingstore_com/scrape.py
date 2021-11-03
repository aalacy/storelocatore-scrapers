import re
import csv
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

    DOMAIN = "gopackagingstore.com"
    start_url = "https://www.gopackagingstore.com/search"

    response = session.get(start_url)
    dom = etree.HTML(response.text)
    all_locations = dom.xpath('//span[@itemprop="name"]/a/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        loc_response = session.get(store_url)
        loc_dom = etree.HTML(loc_response.text)

        raw_address = loc_dom.xpath('//div[@class="adr"]//text()')
        raw_address = [elem.strip() for elem in raw_address if elem.strip()]
        location_name = loc_dom.xpath(
            '//span[@class="content_frame"]//div[@class="view-content"]/div/text()'
        )
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = raw_address[0]
        location_type = "<MISSING>"
        city = raw_address[1]
        state = raw_address[-1].split()[0]
        zip_code = raw_address[-1].split()[-1]
        country_code = "<MISSING>"
        store_number = store_url.split("/")[-1]
        phone = loc_dom.xpath('//span[@itemprop="telephone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        latitude = re.findall('latitude":"(.+?)",', loc_response.text)
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = re.findall('longitude":"(.+?)",', loc_response.text)
        longitude = longitude[0] if longitude else "<MISSING>"
        hours_of_operation = loc_dom.xpath(
            '//h2[contains(text(), "Location Hours")]/following-sibling::div/text()'
        )
        hours_of_operation = (
            hours_of_operation[0].strip() if hours_of_operation else "<MISSING>"
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
