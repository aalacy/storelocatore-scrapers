import re
import csv
from lxml import etree

from sgselenium import SgFirefox


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
    items = []

    start_url = "https://www.hotboxpizza.com/hotbox-pizza-locations/"
    domain = re.findall(r"://(.+?)/", start_url)[0].replace("www.", "")
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//a[contains(@href, "hotbox-pizza-locations")]/@href')
    for store_url in all_locations[1:-1]:
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        location_name = loc_dom.xpath('//h1[@itemprop="headline"]/text()')
        if not location_name:
            location_name = loc_dom.xpath('//div[@class="avia_textblock  "]/h2/text()')
        if not location_name:
            location_name = loc_dom.xpath('//h2[@itemprop="headline"]/text()')
        location_name = location_name[0] if location_name else "<MISSING>"
        raw_data = loc_dom.xpath('//script[@class="av-php-sent-to-frontend"]/text()')[0]
        street_address = re.findall("address'] = (.+?);", raw_data)[0][1:-1]
        city = re.findall(r"city'] = (.+?);", raw_data)[0][1:-1].capitalize()
        state = re.findall(r"state'] = (.+?);", raw_data)[0][1:-1]
        zip_code = re.findall(r"postcode'] = (.+?);", raw_data)[0]
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        latitude = re.findall(r"lat'] = (.+?);", raw_data)[0]
        longitude = re.findall(r"long'] = (.+?);", raw_data)[0]
        hoo = loc_dom.xpath('//p[strong[contains(text(), "Hours:")]]/text()')
        if not hoo:
            hoo = loc_dom.xpath('//p[contains(text(), "am-")]/text()')
        hoo = [e.strip() for e in hoo if e.strip()]
        hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"

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
