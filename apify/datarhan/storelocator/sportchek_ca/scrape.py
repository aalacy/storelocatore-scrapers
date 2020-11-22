import re
import csv
import json
import sgzip
import urllib.parse
from lxml import etree
from sgzip import SearchableCountries

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

    DOMAIN = 'sportchek.ca'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}

    start_url = 'https://www.sportchek.ca/campaigns/stores/locations.html'
    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_stores_html = dom.xpath('//li[@itemtype="http://schema.org/LocalBusiness"]')
    for store_html in all_stores_html:
        store_url = 'https://www.sportchek.ca' + store_html.xpath('.//h4/a/@href')[0]
        location_name = store_html.xpath('.//h4/a/text()')[0]
        location_name = location_name if location_name else '<MISSING>'
        street_address = store_html.xpath('.//p[@itemprop="streetAddress"]/text()')[0]
        street_address = street_address if street_address else '<MISSING>'
        city = store_html.xpath('.//span[@itemprop="addressLocality"]/text()')[0]
        city = city if city else '<MISSING>'
        state = store_html.xpath('.//span[@itemprop="addressRegion"]/text()')[0]
        state = state if state else '<MISSING>'
        zip_code = store_html.xpath('.//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else '<MISSING>'
        country_code = ''
        country_code = country_code if country_code else '<MISSING>'
        phone = store_html.xpath('.//p[@itemprop="telephone"]/a/text()')[0]
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        
        store_response = session.get(store_url, headers=headers)
        store_dom = etree.HTML(store_response.text)
        hours_of_operation = store_dom.xpath('.//div[contains(@class, "store-hours")]/p/text()')
        hours_of_operation = [elem.strip() for elem in hours_of_operation if elem.strip()]
        hours_of_operation = ', '.join(hours_of_operation) if hours_of_operation else '<MISSING>'
        geo_data = store_dom.xpath('//div/@data-info')
        if not geo_data:
            latitude = '<MISSING>'
            longitude = '<MISSING>'
            store_number = '<MISSING>'
        else:
            geo_data = geo_data[0]
            if geo_data[-1] != '}':
                latitude = re.findall('latitude": (.+?),', store_response.text)[0]
                latitude = latitude if latitude else '<MISSING>'
                longitude = re.findall('longitude": (.+?)}', store_response.text)[0]
                longitude = longitude if longitude else '<MISSING>'
                store_number = re.findall('storeId": (.+), "name', store_response.text)
                store_number = store_number[0] if store_number else '<MISSING>'
            else:
                geo_data = json.loads(geo_data)
                latitude = geo_data['latitude']
                latitude = latitude if latitude else '<MISSING>'
                longitude = geo_data['longitude']
                longitude = longitude if longitude else '<MISSING>'
                store_number = geo_data['name']
                store_number = store_number if store_number else '<MISSING>'

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
