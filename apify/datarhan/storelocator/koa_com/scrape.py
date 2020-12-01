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
    scraped_stores = []

    DOMAIN = 'koa.com'

    start_url = 'https://koa.com/campgrounds/'
    
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    
    all_urls = dom.xpath('//ul[@class="zebra-list"]/li/div//a/@href')
    for url in all_urls:
        full_location_url = 'https://koa.com' + url
        location_response = session.get(full_location_url)
        location_dom = etree.HTML(location_response.text)
        location_data = location_dom.xpath('//script[@type="application/ld+json"]/text()')[0]
        location_data = json.loads(location_data)

        store_url = full_location_url
        store_url = store_url if store_url else '<MISSING>'
        location_name = location_data['name']
        location_name = location_name if location_name else '<MISSING>'
        street_address = location_data['address']['streetAddress']
        street_address = street_address if street_address else '<MISSING>'
        city = location_data['address']['addressLocality']
        city = city if city else '<MISSING>'
        state = location_data['address']['addressRegion']
        state = state if state else '<MISSING>'
        zip_code = location_data['address']['postalCode']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = location_data['address']['addressCountry']
        country_code = country_code if country_code else '<MISSING>'
        store_number = ''
        store_number = store_number if store_number else '<MISSING>'
        phone = location_data['telephone']
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = location_data['geo']['latitude']
        latitude = latitude if latitude else '<MISSING>'
        longitude = location_data['geo']['longitude']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = '<MISSING>'
        
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
