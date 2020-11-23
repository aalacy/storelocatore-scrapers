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
    scraped_locations = []

    DOMAIN = 'dutchbros.com'

    start_url = 'https://files.dutchbros.com/api-cache/stands.json'
    
    response = session.get(start_url)
    all_poi = json.loads(response.text)
    
    for poi in all_poi:
        store_url = ''
        store_url = store_url if store_url else '<MISSING>'
        location_name = poi['store_nickname']
        location_name = location_name if location_name else '<MISSING>'
        street_address = poi['stand_address']
        street_address = street_address if street_address else '<MISSING>'
        city = poi['city']
        city = city if city else '<MISSING>'
        state = poi['state']
        state = state if state else '<MISSING>'
        zip_code = poi['zip_code']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = ''
        country_code = country_code if country_code else '<MISSING>'
        store_number = poi['store_number']
        store_number = store_number if store_number else '<MISSING>'
        phone = ''
        phone = phone if phone else '<MISSING>'
        location_type = ''
        if poi['drivethru'] == '1':
            location_type = 'drivethru'
        location_type = location_type if location_type else '<MISSING>'
        latitude = poi['lat']
        latitude = latitude if latitude else '<MISSING>'
        longitude = poi['lon']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = poi['hours']
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

        if store_number not in scraped_locations:
            scraped_locations.append(store_number)
            items.append(item)
    
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
