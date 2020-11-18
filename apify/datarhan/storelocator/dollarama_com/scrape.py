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

    DOMAIN = 'dollarama.com'

    start_url = 'https://www.dollarama.com/en-CA/locations/GetDataByCoordinates?longitude=-75.979099&latitude=44.352511&distance=30000&units=kilometers&amenities=&paymentMethods='
    response = session.get(start_url)
    
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
        store_url = 'https://www.dollarama.com/en-{}/locations/{}/{}-{}'.format(country_code, state, city, street_address.replace(' ', '-'))

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

        items.append(item)

    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
