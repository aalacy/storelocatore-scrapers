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
    scraped_items = []

    DOMAIN = 'dollarama.com'

    hdr = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    start_url = 'https://www.dollarama.com/en-CA/locations/GetDataByCoordinates?longitude={}&latitude={}&distance=500&units=kilometers&amenities=&paymentMethods='
    all_coordinates = []
    us_coordinates = sgzip.coords_for_radius(radius=100, country_code=SearchableCountries.USA)
    for coord in us_coordinates:
        all_coordinates.append(coord)
    ca_coordinates = sgzip.coords_for_radius(radius=100, country_code=SearchableCountries.CANADA)
    for coord in ca_coordinates:
        all_coordinates.append(coord)
    # all_coordinates += [('-113.610733', '53.621822'), ('-113.32064', '53.51353')]

    for coord in tqdm(all_coordinates):
        lat, lng = coord
        response = session.post(start_url.format(lng, lat), headers=hdr)
        
        all_poi_data = json.loads(response.text)
        for poi in all_poi_data['StoreLocations']:
            location_name = poi['Name']
            location_name = location_name if location_name else '<MISSING>'
            street_address = poi['ExtraData']['Address']['AddressNonStruct_Line1']
            if poi['ExtraData']['Address']['AddressNonStruct_Line2']:
                street_address += ', ' + poi['ExtraData']['Address']['AddressNonStruct_Line2'] 
            street_address = street_address if street_address else '<MISSING>'
            city = poi['ExtraData']['Address']['Locality']
            city = city if city else '<MISSING>'
            state = poi['ExtraData']['Address']['Region']
            state = state if state else '<MISSING>'
            zip_code = poi['ExtraData']['Address']['PostalCode']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = poi['ExtraData']['Address']['CountryCode']
            country_code = country_code if country_code else '<MISSING>'
            store_number = poi['LocationNumber']
            store_number = store_number if store_number else '<MISSING>'
            phone = poi['ExtraData']['Phone']
            phone = phone if phone else '<MISSING>'
            location_type = poi['Location']['type']
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi['Location']['coordinates'][-1]
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi['Location']['coordinates'][0]
            longitude = longitude if longitude else '<MISSING>'
            store_url = 'https://www.dollarama.com/en-CA/locations/{}/{}-{}'.format(
                state.replace(' ', '-').replace('.', ''),
                city.replace(' ', '-').replace('.', ''),
                street_address.split(',')[0].replace(' ', '-').replace('.', '')
            )

            hours_of_operation = []
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            hours = poi['ExtraData']['Hours of operations'].split('|')
            hours_of_operation = list(map(lambda d, h: d + ' ' + h, days, hours))
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

            if store_number not in scraped_items:
                scraped_items.append(store_number)
                items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
