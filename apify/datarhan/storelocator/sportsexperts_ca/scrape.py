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

    DOMAIN = 'sportsexperts.ca'

    start_url = 'https://www.sportsexperts.ca/fr-CA/Magasins'
    headers = {
        'Host': 'www.sportsexperts.ca',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36',
    }

    response = session.get(start_url, headers=headers)
    dom = etree.HTML(response.text)

    all_stores_urls = dom.xpath('//div[@class="store-info"]/a/@href')
    for url in all_stores_urls:
        store_response = session.get(url, headers=headers)
        store_dom = etree.HTML(store_response.text)

        store_data = store_dom.xpath('//div[@data-oc-controller="StoreLocator"]/@data-context')[0]
        store_data = json.loads(store_data)

        store_url = url
        location_name = store_data['StoreName']
        location_name = location_name if location_name else '<MISSING>'
        street_address = store_data['Address']['Line1']
        if store_data['Address']['Line2']:
            street_address += ', ' + store_data['Address']['Line2']
        street_address = street_address if street_address else '<MISSING>'
        city = store_data['Address']['City']
        city = city if city else '<MISSING>'
        state = store_data['Address']['RegionCode']
        state = state if state else '<MISSING>'
        zip_code = store_data['Address']['PostalCode']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = store_data['Address']['CountryCode']
        country_code = country_code if country_code else '<MISSING>'
        store_number = store_data['StoreNumber']
        store_number = store_number if store_number else '<MISSING>'
        phone = store_data['PhoneNumber']
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = store_data['Address']['Latitude']
        latitude = latitude if latitude else '<MISSING>'
        longitude = store_data['Address']['Longitude']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = []
        for elem in store_data['OpeningHours']['OpeningHoursByDay']:
            day = elem['Day']
            open_hours = elem['StartingTime']
            close_hours = elem['EndingTime']
            hours_of_operation.append('{} {} - {}'.format(day, open_hours, close_hours))
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

        if store_number not in scraped_items:
            scraped_items.append(store_number)
            items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
