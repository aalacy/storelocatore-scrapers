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

    DOMAIN = 'autovalue.com'
    
    all_codes = []
    ca_zips = sgzip.for_radius(radius=100, country_code=SearchableCountries.CANADA)
    for zip_code in ca_zips:
        all_codes.append(zip_code)

    start_url = 'https://api.marks.com/hy/v1/marks/storelocators/bopis/nearLocation/filtered?location={}&pageSize=500'
    for code in all_codes:
        response = session.get(start_url.format(code.replace(' ', '+')))
        data = json.loads(response.text)
        
        all_poi = data['pointsOfService']
        for poi in all_poi:
            store_url = [elem['value'] for elem in poi['urlLocalized'] if elem['locale'] == 'en']
            store_url = urllib.parse.urljoin(start_url, store_url[0]) if store_url else '<MISSING>'
            location_name = poi['displayName']
            location_name = location_name if location_name else '<MISSING>'
            street_address = poi['address']['line1']
            if poi['address']['line2']:
                street_address += ', ' + poi['address']['line2']
            street_address = street_address if street_address else '<MISSING>'
            city = poi['address']['town']
            city = city if city else '<MISSING>'
            state = poi['address']['province']
            state = state if state else '<MISSING>'
            zip_code = poi['address']['postalCode']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = poi['address']['country']['isocode']
            country_code = country_code if country_code else '<MISSING>'
            store_number = poi['name']
            store_number = store_number if store_number else '<MISSING>'
            phone = poi.get('phone')
            phone = phone if phone else '<MISSING>'
            location_type = ''
            location_type = location_type if location_type else '<MISSING>'
            latitude = poi['geoPoint']['latitude']
            latitude = latitude if latitude else '<MISSING>'
            longitude = poi['geoPoint']['longitude']
            longitude = longitude if longitude else '<MISSING>'
            hours_of_operation = poi.get('workingHours')
            hours_of_operation = hours_of_operation if hours_of_operation else '<MISSING>'
            
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
