import re
import csv
import json
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

    DOMAIN = 'peopleready.com'

    start_url = 'https://www.peopleready.com/api/location/getnearestbranches'
    body = '{"Latitude":53.77450934032745,"Longitude":-121.70410083292569,"DiameterToSearch":60000,"Skip":0}'
    headers = {
        'authority': 'www.peopleready.com',
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json;charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36'
    }
    
    response = session.post(start_url, data=body, headers=headers)
    all_poi = json.loads(response.text)

    for poi in all_poi:
        store_url = 'https://www.peopleready.com/locations' + poi['Url']
        location_name = poi['Title']
        location_name = location_name if location_name else '<MISSING>'
        street_address = poi['Address']['Street']
        street_address = street_address if street_address else '<MISSING>'
        city = poi['Address']['City']
        city = city if city else '<MISSING>'
        state = poi['Address']['StateCode']
        state = state if state else '<MISSING>'
        zip_code = poi['Address']['Zip']
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = poi['Address']['CountryCode']
        country_code = country_code if country_code else '<MISSING>'
        store_number = poi['BranchNumber']
        store_number = store_number if store_number else '<MISSING>'
        phone = poi['PhoneNumber']
        phone = phone if phone else '<MISSING>'
        location_type = ''
        location_type = location_type if location_type else '<MISSING>'
        latitude = poi['Address']['Latitude']
        latitude = latitude if latitude else '<MISSING>'
        longitude = poi['Address']['Longitude']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = []
        hours = {}
        for key, value in poi.items():
            if key.endswith('Close'):
                day = key.replace('Close', '')
                if hours.get(day):
                    hours[day]['close'] = value
                    if not value.strip():
                        hours[day] = {'close': 'closed'}
                else:
                    hours[day] = {'close': value}
                    if not value.strip():
                        hours[day] = {'close': 'closed'}
            if key.endswith('Open'):
                day = key.replace('Open', '')
                if hours.get(day):
                    hours[day]['open'] = value
                    if not value.strip():
                        hours[day] = {'open': 'closed'}
                else:
                    hours[day] = {'open': value}
                    if not value.strip():
                        hours[day] = {'open': 'closed'}
        for day, hours in hours.items():
            if not hours.get('open'):
                hours_of_operation.append('{} - closed'.format(day))
            else:
                hours_of_operation.append('{} {} - {}'.format(day, hours['open'], hours['close']))
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

        items.append(item)
        
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
