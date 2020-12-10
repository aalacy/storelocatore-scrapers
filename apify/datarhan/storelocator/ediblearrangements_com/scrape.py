import csv
import json
from lxml import etree

from sgrequests import SgRequests

DOMAIN = 'ediblearrangements.com'


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    
    url = 'https://www.ediblearrangements.com/stores/store-locator.aspx/GetStoresList'
    payload = "{'AreaName':'68874','Distance':'50000'}"
    headers = {
        'authority': 'www.ediblearrangements.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
        'content-type': 'application/json; charset=UTF-8',
        'origin': 'https://www.ediblearrangements.com',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    allpoints_response = session.post(url, data=payload, headers=headers)
    all_data = json.loads(allpoints_response.text)
    all_data = json.loads(all_data['d'])
    
    for point_data in all_data['_Data']:
        store_url = 'https://www.ediblearrangements.com/stores/{}'.format(point_data['PageFriendlyURL']) 
        location_name = point_data['FormalName']
        location_name = location_name if location_name else '<MISSING>'
        street_address = point_data['Address'].split('<br>')[0]
        street_address = street_address if street_address else '<MISSING>'
        city = point_data['Address'].split('<br>')[-1].split(',')[0].strip()
        city = city if city else '<MISSING>'
        state = point_data['Address'].split('<br>')[-1].split(',')[-1].strip().split()[0]
        state = state if state else '<MISSING>'
        zip_code = point_data['Address'].split('<br>')[-1].split(',')[-1].strip().split()[-1]
        zip_code = zip_code if zip_code else '<MISSING>'
        country_code = '<MISSING>'
        country_code = country_code if country_code else '<MISSING>'
        store_number = point_data['Number']
        phone = point_data['PhoneNumber']
        phone = phone if phone else '<MISSING>'
        location_type = '<MISSING>'
        latitude = point_data['Latitude']
        latitude = latitude if latitude else '<MISSING>'
        longitude = point_data['Longitude']
        longitude = longitude if longitude else '<MISSING>'
        hours_of_operation = point_data['TimingsShort']
        all_hours = []
        for elem in hours_of_operation:
            all_hours.append('{} - {}'.format(elem['Days'], elem['Timing']))
        if all_hours:
            hours_of_operation = '; '.join(all_hours)

        street_address = street_address.replace(state, '').replace(zip_code, '')

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


hdr = {
    'authority': 'www.ediblearrangements.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,pt;q=0.6',
    'content-type': 'application/json; charset=UTF-8',
    'origin': 'https://www.ediblearrangements.com',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}