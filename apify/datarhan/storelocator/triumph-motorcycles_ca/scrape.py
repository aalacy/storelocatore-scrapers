import re
import csv
import json
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

    DOMAIN = 'triumph-motorcycles.ca'

    start_url = 'https://www.triumph-motorcycles.ca/dealers/find-a-dealer?market=6&viewall=true'

    response = session.get(start_url)
    dom = etree.HTML(response.text)

    all_poi_html = dom.xpath('//div[@class="dealerListItem"]')
    for poi_html in all_poi_html:
        store_url = poi_html.xpath('.//div[@class="websiteAddress"]//a/text()')
        store_url = store_url[0] if store_url else '<MISSING>'
        location_name = poi_html.xpath('.//span[@class="dealerName"]/text()')
        location_name = location_name[0] if location_name else '<MISSING>'

        location_response = session.get(store_url)
        location_dom = etree.HTML(location_response.text)
        address_raw = location_dom.xpath('//div[@class="span4 dealerAddress"]/p/text()')
        address_raw = [elem.strip() for elem in address_raw if elem.strip()]
        address_raw = [elem for elem in address_raw if elem != ',']
        if len(address_raw) == 2:
            elem_1 = address_raw[0].split('\r\n')[0]
            elem_3 = address_raw[0].split()[-1]
            elem_2 = address_raw[0].replace(elem_1, '').replace(elem_3, '').replace('\r\n', ' ').strip()
            address_raw = [elem_1, elem_2, elem_3]
        if len(address_raw) == 4:
            address_raw = [' '.join(address_raw[:2])] + address_raw[2:]
        if len(address_raw) == 5:
            address_raw = [address_raw[0]] + address_raw[-2:]
        street_address = address_raw[0].replace(',', '')
        street_address = street_address if street_address else '<MISSING>'
        city = ' '.join(address_raw[1].split()[:-1]).strip()
        city = city if city else '<MISSING>'
        state = address_raw[1].split()[-1].strip()
        state = state if state else '<MISSING>'
        if '\r\n' in street_address:
            city = street_address.split('\r\n')[-1]
            street_address = street_address.split('\r\n')[0]
            state = address_raw[1].split()[0].strip()
        zip_code = address_raw[-1]
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = ''
        country_code = country_code if country_code else '<MISSING>'
        store_number = ''
        store_number = store_number if store_number else '<MISSING>'
        phone = poi_html.xpath('.//div[@class="dealerContact"]/span/text()')[1]
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        
        geo_data = location_dom.xpath('//script[contains(text(), "LatLng")]/text()')[0]
        geo_data = re.findall('LatLng\((.+?)\);', geo_data)[0]
        latitude = geo_data.split(',')[0]
        latitude = latitude if latitude else '<MISSING>'
        longitude = geo_data.split(',')[-1]
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = location_dom.xpath('//div[@class="span4 dealerOpeningTimes"]/p[1]/text()')
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
