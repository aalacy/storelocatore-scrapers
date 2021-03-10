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

    start_url = "https://www.adventhealth.com/find-a-location"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath(
        '//h3[@class="location-block__name h2 notranslate "]/a/@href'
    )
    next_page = dom.xpath('//a[@rel="next"]/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath(
            '//h3[@class="location-block__name h2 notranslate "]/a/@href'
        )
        next_page = dom.xpath('//a[@rel="next"]/@href')

    for url in all_locations:
        store_url = urljoin(start_url, url)
        if "adventhealth.com" not in url:
            continue
        loc_response = session.get(store_url)
        print(store_url, loc_response.status_code)
        loc_dom = etree.HTML(loc_response.text)

        location_name = dom.xpath(
            '//span[@class="location-bar__name-text notranslate"]/text()'
        )
        location_name = location_name[0].strip() if location_name else "<MISSING>"
        if location_name.endswith(","):
            location_name = location_name[:-1]
        street_address = loc_dom.xpath('//span[@property="streetAddress"]/text()')
        street_address = street_address[0].strip() if street_address else "<MISSING>"
        if street_address.endswith(","):
            street_address = street_address[:-1]
        city = loc_dom.xpath('//span[@property="addressLocality"]/text()')
        city = city[0] if city else "<MISSING>"
        state = loc_dom.xpath('//span[@property="addressRegion"]/text()')
        state = state[0] if state else "<MISSING>"
        zip_code = loc_dom.xpath('//span[@property="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else "<MISSING>"
        country_code = re.findall('country":"(.+?)",', loc_response.text)
        country_code = country_code[0] if country_code else "<MISSING>"
        store_number = "<MISSING>"
        phone = loc_dom.xpath('//a[@class="telephone"]/text()')
        phone = phone[0].strip() if phone and phone[0].strip() else "<MISSING>"
        location_type = "<MISSING>"
        latitude = loc_dom.xpath("//@data-lat")
        latitude = latitude[0] if latitude else "<MISSING>"
        longitude = loc_dom.xpath("//@data-lng")
        longitude = longitude[0] if longitude else "<MISSING>"
        hoo = loc_dom.xpath('//div[@class="location-block__office-hours-hours"]/text()')
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
