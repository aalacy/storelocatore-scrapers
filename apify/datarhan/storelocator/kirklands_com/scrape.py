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

    DOMAIN = 'kirklands.com'

    start_url = 'https://www.kirklands.com/custserv/locate_store.cmd?icid=hlink6b_ao_store+locator_N'
    
    response = session.get(start_url)
    dom = etree.HTML(response.text)
    
    all_urls = dom.xpath('//div[@id="stateListing"]//a/@href')
    for url in all_urls:
        full_location_url = 'https://www.kirklands.com' + url
        location_response = session.get(full_location_url)
        location_dom = etree.HTML(location_response.text)

        store_url = full_location_url
        store_url = store_url if store_url else '<MISSING>'
        location_name = location_dom.xpath('//h1[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else '<MISSING>'
        street_address = location_dom.xpath('//span[@itemprop="streetAddress"]/text()')
        street_address = street_address[0].strip() if street_address else '<MISSING>'
        city = location_dom.xpath('//span[@itemprop="addressLocality"]/text()')[-1]
        city = city if city else '<MISSING>'
        state = location_dom.xpath('//span[@itemprop="addressRegion"]/text()')
        state = state[0].strip() if state else '<MISSING>'
        zip_code = location_dom.xpath('//span[@itemprop="postalCode"]/text()')
        zip_code = zip_code[0] if zip_code else '<MISSING>'
        country_code = ''
        country_code = country_code if country_code else '<MISSING>'
        store_number = ''
        store_number = store_number if store_number else '<MISSING>'
        phone = location_dom.xpath('//span[@itemprop="telephone"]/text()')
        phone = phone[0] if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = location_dom.xpath('//meta[@itemprop="latitude"]/@content')
        latitude = latitude[0] if latitude else '<MISSING>'
        longitude = location_dom.xpath('//meta[@itemprop="longitude"]/@content')
        longitude = longitude[0] if longitude else '<MISSING>'
        hours_of_operation = []
        hours_html = location_dom.xpath('//div[@class="hours"]//time//tr[th[@id="day-0"]]/th')
        for elem in hours_html:
            day = elem.xpath('.//text()')[0]
            hours_close = location_dom.xpath('.//meta[@itemprop="closes"]/@content')[0]
            hours_open = location_dom.xpath('.//meta[@itemprop="opens"]/@content')[0]
            hours_of_operation.append('{} {} - {}'.format(day, hours_close, hours_open))
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
