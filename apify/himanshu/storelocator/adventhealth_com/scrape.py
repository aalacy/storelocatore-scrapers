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
    scraped_items = []

    start_url = "https://www.adventhealth.com/find-a-location"
    domain = re.findall("://(.+?)/", start_url)[0].replace("www.", "")

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_locations = dom.xpath('//li[@class="facility-search-block__item"]')
    next_page = dom.xpath('//a[@rel="next"]/@href')
    while next_page:
        response = session.get(urljoin(start_url, next_page[0]))
        dom = etree.HTML(response.text)
        all_locations += dom.xpath('//li[@class="facility-search-block__item"]')
        next_page = dom.xpath('//a[@rel="next"]/@href')

    for poi_html in all_locations:
        store_url = poi_html.xpath(".//h3/a/@href")
        if not store_url:
            store_url = poi_html.xpath('.//a[contains(text(), "View Website")]/@href')
        store_url = urljoin(start_url, store_url[0]) if store_url else "<MISSING>"
        if "adventhealth.com" in store_url:
            loc_response = session.get(store_url)
            loc_dom = etree.HTML(loc_response.text)

            location_name = loc_dom.xpath(
                '//span[@class="location-bar__name-text notranslate"]/text()'
            )
            location_name = location_name[0].strip() if location_name else "<MISSING>"
            if location_name.endswith(","):
                location_name = location_name[:-1]
            street_address = loc_dom.xpath('//span[@property="streetAddress"]/text()')
            street_address = (
                street_address[0].strip() if street_address else "<MISSING>"
            )
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
            hoo = loc_dom.xpath(
                '//div[@class="location-block__office-hours-hours"]/text()'
            )
            hoo = [e.strip() for e in hoo if e.strip()]
            hours_of_operation = " ".join(hoo) if hoo else "<MISSING>"
        else:
            location_name = poi_html.xpath(".//h3/a/text()")
            location_name = location_name[0].strip() if location_name else "<MISSING>"
            street_address = poi_html.xpath('.//span[@property="streetAddress"]/text()')
            street_address = (
                street_address[0].strip() if street_address else "<MISSING>"
            )
            city = poi_html.xpath('.//span[@property="addressLocality"]/text()')
            city = city[0] if city else "<MISSING>"
            state = poi_html.xpath('.//span[@property="addressRegion"]/text()')
            state = state[0] if state else "<MISSING>"
            zip_code = poi_html.xpath('.//span[@property="postalCode"]/text()')
            zip_code = zip_code[0] if zip_code else "<MISSING>"
            country_code = re.findall('country":"(.+?)",', loc_response.text)
            country_code = country_code[0] if country_code else "<MISSING>"
            store_number = "<MISSING>"
            phone = poi_html.xpath('.//a[@class="telephone"]/text()')
            phone = phone[0].strip() if phone and phone[0].strip() else "<MISSING>"
            location_type = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
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
