import csv
import json
import sgzip
import urllib.parse
from lxml import etree
from sgzip import SearchableCountries

from tqdm import tqdm

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

    DOMAIN = 'jcpenney.com'

    hdr = {
        'authority': 'browse-api.jcpenney.com',
        'method': 'GET',
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
        'accept-version': '1',
        'origin': 'https://www.jcpenney.com',
        'referer': 'https://www.jcpenney.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        'x-jcp-forwarded-channel': 'true',
        'x-jcp-forwarded-host': 'browse-api.jcpenney.com',
        'x-jcp-forwarded-proto': 'https'
    }

    all_codes = []
    us_zips = sgzip.for_radius(radius=200, country_code=SearchableCountries.USA)
    for zip_code in us_zips:
        all_codes.append(zip_code)
    ca_zips = sgzip.for_radius(radius=200, country_code=SearchableCountries.CANADA)
    for zip_code in ca_zips:
        all_codes.append(zip_code)

    start_url = 'https://browse-api.jcpenney.com/v1/stores?radius=1000&pageSize=100&storeService=&location={}'
    for code in tqdm(all_codes):
        response = session.get(start_url.format(code))
        if response.status_code != 200:
            print('CODE NOT 200 for {}'.format(start_url.format(code)))
        data = json.loads(response.text)
        if not data.get('stores'):
            continue
        
        all_poi = data['stores']
        
        for page_url in data['page']:
            page_response = session.get(page_url['url'])
            page_data = json.loads(page_response.text)
            if page_data.get('stores'):
                all_poi += page_data['stores']
        
        for poi in all_poi:
            store_url = poi.get('storePageUrl')
            store_url = store_url if store_url else '<MISSING>'
            location_name = poi['name']
            location_name = location_name if location_name else '<MISSING>'
            street_address = poi['street']
            street_address = street_address if street_address else '<MISSING>'
            city = poi['city']
            city = city if city else '<MISSING>'
            state = poi['state']
            state = state if state else '<MISSING>'
            zip_code = poi['zip']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = poi['country']
            if country_code == 'PUERTO RICO':
                continue 
            country_code = country_code if country_code else '<MISSING>'
            store_number = poi['number']
            store_number = store_number if store_number else '<MISSING>'
            phone = poi['phone']
            phone = phone if phone else '<MISSING>'
            location_type = poi['type']
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi['latitude']
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi['longitude']
            longitude = longitude if longitude else '<MISSING>'
            hours_of_operation = []
            for elem in poi['timings']:
                hours_of_operation.append('{} - {}'.format(elem['days'], elem['time']))
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

            check = '{} {}'.format(store_number, street_address)
            if check not in scraped_stores:
                scraped_stores.append(check)
                items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
