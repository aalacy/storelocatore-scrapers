import csv
import json
import zipcodes
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

    DOMAIN = 'victra.com'

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
        'Connection': 'keep-alive',
        'Host': 'victra.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    start_url = 'https://victra.com/Handlers/LocationData.ashx?origAddress=US'
    response = session.get(start_url, headers=headers)
    
    all_poi = json.loads(response.text)
    for poi in all_poi:
        store_url = '<MISSING>'
        location_name = poi['name']
        location_name = location_name if location_name else '<MISSING>'
        street_address = poi['address']
        street_address = street_address if street_address else '<MISSING>'
        city = poi['city']
        city = city if city else '<MISSING>'
        state = poi['state']
        state = state if state else '<MISSING>'
        zip_code = poi['postal']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = ''
        country_code = country_code if country_code else '<MISSING>'
        store_number = poi['id']
        store_number = store_number if store_number else '<MISSING>'
        phone = poi['phone']
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = poi['lat']
        latitude = latitude if latitude else '<MISSING>'
        longitude = poi['lng']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = []
        for key, value in poi.items():
            if 'hours' in key:
                hours_of_operation.append('{}: {}'.format(key.split('_')[0], value))
        hours_of_operation = ', '.join(hours_of_operation)
        
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
