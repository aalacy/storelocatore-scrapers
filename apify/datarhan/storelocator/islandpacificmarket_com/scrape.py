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

    start_url = "https://islandpacificmarket.com/stores/"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")
    
    with SgFirefox() as driver:
        driver.get(start_url)
        dom = etree.HTML(driver.page_source)

    all_locations = dom.xpath('//div[@class="sabai-directory-photos"]/a/@href')
    for store_url in all_locations:
        with SgFirefox() as driver:
            driver.get(store_url)
            loc_dom = etree.HTML(driver.page_source)

        location_name = loc_dom.xpath('//meta[@itemprop="name"]/@content')
        location_name = location_name[0] if location_name else "<MISSING>"
        street_address = loc_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0] if street_address else "<MISSING>"
        city = loc_dom.xpath('//span[@itemprop="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = loc_dom.xpath('//span[@itemprop="addressCountry"]/text()')
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath(
            '//div[@class="sabai-directory-contact-tel"]/span[@itemprop="telephone"]/text()'
        )
        phone = phone[0] if phone else "<MISSING>"
        location_type = "<MISSING>"
        geo = loc_dom.xpath('//script[contains(text(), "GoogleMaps")]/text()')[0]
        latitude = re.findall('lat":(.+?),', geo)[0]
        longitude = re.findall('lng":(.+?),', geo)[0]
        hoo = loc_dom.xpath('//p[contains(text(), "Hours:")]/text()')
        hours_of_operation = hoo[0].replace("Hours: ", "") if hoo else "<MISSING>"

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
