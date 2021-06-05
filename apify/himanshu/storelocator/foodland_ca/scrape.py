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
    scraped_items = []

    start_url = "https://foodland.ca/store-locator/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    hdr = {
        "accept": "*/*",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//a[@class="store-title"]/@href')
    for store_url in all_locations:
        loc_response = session.get(store_url, headers=hdr)
        loc_dom = etree.HTML(loc_response.text)

        location_name = loc_dom.xpath('//span[@class="fl-heading-text"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath(
            '//span[@class="location_address_address_1"]/text()'
        )
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@class="city"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@class="province"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@class="postal_code"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//span[@class="phone"]/a/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//div/@data-lat")[0]
        longitude = loc_dom.xpath("//div/@data-lng")[0]
        hoo = loc_dom.xpath('//div[@class="hours"]/table//text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo[2:]) if hoo else "<MISSING>"
        if hours_of_operation == "<MISSING>":
            hours_of_operation = "Open 24 Hours"

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
        check = f"{location_name} {street_address}"
        if check not in scraped_items:
            scraped_items.append(check)
            items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
