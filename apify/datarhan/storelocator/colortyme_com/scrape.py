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

    DOMAIN = 'colortyme.com'

    start_url = 'https://www.colortyme.com/features/AllLocationsColorTyme.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)
    
    all_poi_html = dom.xpath('//div[@itemtype="http://schema.org/LocalBusiness"]')
    for poi in all_poi_html:
        store_url = poi.xpath('.//a[contains(text(), "Website")]/@href') 
        store_url = urllib.parse.urljoin(start_url, store_url[0]) if store_url else '<MISSING>'
        location_name = poi.xpath('.//h1[@itemprop="name"]/text()')
        location_name = location_name[0] if location_name else '<MISSING>'
        street_address = poi.xpath('.//div//text()')
        street_address = street_address[0].strip() if street_address else '<MISSING>'
        city = poi.xpath('.//div//text()')
        city = city[-1].split(',')[0] if city else '<MISSING>'
        state_raw = poi.xpath('.//div//text()')
        state = state_raw[-1].split(',')[-1].split()[0].strip()
        if len(state) > 2:
            state = state_raw[-1].split()[1]
            city = state_raw[-1].split()[0]
        zip_code = state_raw[-1].split(',')[-1].split()[-1].strip()
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = ''
        country_code = country_code if country_code else '<MISSING>'
        store_number = ''
        store_number = store_number if store_number else '<MISSING>'
        phone = poi.xpath('.//a[contains(@href, "tel")]/text()')
        phone = phone[0] if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = ''
        latitude = latitude if latitude else '<MISSING>'
        longitude = ''
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = poi.xpath('.//time/@datetime')
        hours_of_operation = hours_of_operation[0] if hours_of_operation else '<MISSING>'
        
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
