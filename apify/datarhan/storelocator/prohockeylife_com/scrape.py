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

    DOMAIN = 'https://www.prohockeylife.com/'

    start_url = 'https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=prohockeylife.myshopify.com&latitude=43.413029&longitude=-79.779968&max_distance=0&limit=100&calc_distance=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    response = session.get(start_url, headers=headers)
    data = json.loads(response.text)
    
    for poi in data['stores']:
        store_url = poi['website']
        location_name = poi['name']
        location_name = location_name if location_name else '<MISSING>'
        street_address = poi['address']
        if poi['address2']:
            street_address += ', ' + poi['address2']
        street_address = street_address if street_address else '<MISSING>'
        city = poi['city']
        city = city if city else '<MISSING>'
        state = poi['prov_state']
        state = state if state else '<MISSING>'
        zip_code = poi['postal_zip']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = poi['country']
        country_code = country_code if country_code else '<MISSING>'
        store_number = poi['store_id']
        store_number = store_number if store_number else '<MISSING>'
        phone = poi['phone']
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = poi['lat']
        latitude = latitude if latitude else '<MISSING>'
        longitude = poi['lng']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = poi['hours'].replace('STORE HOURS\r\n', '').replace('\r\n', ', ')
        hours_of_operation = hours_of_operation if hours_of_operation else '<MISSING>'
        if 'TEMPORARILY CLOSED' in hours_of_operation:
            continue

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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
