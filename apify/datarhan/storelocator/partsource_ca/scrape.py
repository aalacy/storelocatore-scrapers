import re
import csv
import urllib.parse
from lxml import etree

from sgrequests import SgRequests


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    session = SgRequests()

    items = []
    scraped_items = []

    DOMAIN = 'partsource.ca'

    start_url = 'https://www.partsource.ca/apps/store-locator/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_stores_html = dom.xpath('//div[@id="addresses_list"]/ul/li')
    for store_html in all_stores_html:
        store_url = store_html.xpath('.//div[@class="store_website"]/a/@href')[0]
        store_response = session.get(store_url, headers=headers)
        store_dom = etree.HTML(store_response.text)

        location_name = store_html.xpath('.//span[@class="name"]/text()')
        location_name = location_name[0].strip() if location_name else '<MISSING>'
        street_address = store_html.xpath('.//span[@class="address"]/text()')[0]
        street_address_2 = store_html.xpath('.//span[@class="address2"]/text()')
        if street_address_2:
            street_address += ', ' + street_address_2[0]
        street_address = street_address if street_address else '<MISSING>'
        city = store_html.xpath('.//span[@class="city"]/text()')
        city = city[0].strip() if city else '<MISSING>'
        state = store_html.xpath('.//span[@class="prov_state"]/text()')
        state = state[0].strip() if state else '<MISSING>'
        zip_code = store_html.xpath('.//span[@class="postal_zip"]/text()')
        zip_code = zip_code[0].strip() if zip_code else '<MISSING>'
        country_code = store_html.xpath('.//span[@class="country"]/text()')
        country_code = country_code[0].strip() if country_code else '<MISSING>'
        store_number = location_name.split('-')[-1].strip()
        store_number = store_number if store_number else '<MISSING>'
        phone = store_html.xpath('.//span[@class="phone"]/text()')
        phone = phone[0].strip() if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = store_dom.xpath('//div/@data-latitude')
        latitude = latitude[0] if latitude else '<MISSING>'
        longitude = store_dom.xpath('//div/@data-longitude')
        longitude = longitude[0] if longitude else '<MISSING>'
        hours_of_operation = []
        hours_html = store_dom.xpath('//div[@data-label="Liquid"]//table//tr')
        for elem in hours_html[1:]:
            day = elem.xpath('.//td/text()')[0]
            hours = elem.xpath('.//td/text()')[-1]
            hours_of_operation.append('{} - {}'.format(day, hours))
        hours_of_operation = ', '.join(hours_of_operation) if hours_of_operation else '<MISSING>'

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
            hours_of_operation
        ]

        items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
