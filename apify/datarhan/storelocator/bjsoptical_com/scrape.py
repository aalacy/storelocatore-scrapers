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

    DOMAIN = 'bjs.com'

    hdr = {
        'authority': 'www.bjs.com',
        'path': '/optical;radius=999999;lat=37.6032972;lng=-77.2635038',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36'
    }

    start_url = 'https://www.bjs.com/optical;radius=999999;lat=37.6032972;lng=-77.2635038'
    response = session.get(start_url, headers=hdr)
    dom = etree.HTML(response.text)
    data = dom.xpath('//script[@id="bjs-universal-app-state"]/text()')[0]
    data = json.loads(data.replace('&q;', '"'))
    all_stores = data['https://api.bjs.com/digital/live/api/v1.2/club/search/10201']['Stores']['PhysicalStore']
    for store_data in all_stores:
        store_url = 'https://www.bjs.com/cl/easton/' + store_data['storeName']
        location_name = store_data['Description'][0]['displayStoreName']
        location_name = location_name if location_name else '<MISSING>'
        street_address = store_data['addressLine']
        street_address = ' '.join(street_address) if street_address else '<MISSING>'
        city = store_data['city']
        city = city if city else '<MISSING>'
        state = store_data['stateOrProvinceName']
        state = state if state else '<MISSING>'
        zip_code = store_data['postalCode']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = store_data['country']
        country_code = country_code if country_code else '<MISSING>'
        store_number = store_data['storeName']
        phone = store_data.get('telephone1')
        phone = phone if phone else '<MISSING>'
        location_type = [elem['value'] for elem in store_data['Attribute'] if elem['name'] == 'StoreType']
        if location_type in ['GAS', 'DC']:
            continue
        location_type = 'optical'
        location_type = location_type if location_type else '<MISSING>'
        latitude = store_data['latitude']
        latitude = latitude if latitude else '<MISSING>'
        longitude = store_data['longitude']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = [elem['value'] for elem in store_data['Attribute'] if elem['name'] == 'Optical Phone Number']
        hours_of_operation = hours_of_operation[0].replace('&l;br&g;', '; ').strip()
        hours_of_operation = hours_of_operation if hours_of_operation else '<MISSING>'
        if hours_of_operation == '0':
            continue
        if 'N/A' in hours_of_operation:
            continue
        check = [elem['value'] for elem in store_data['Attribute'] if 'Optical' in elem['displayValue']]
        if not check:
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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
