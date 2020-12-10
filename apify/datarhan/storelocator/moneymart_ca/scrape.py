
import re
import csv
import json
from sgrequests import SgRequests

DOMAIN = 'moneymart.ca'


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

    response = session.get('https://moneymart.ca/Scripts/StoreLocator.js')
    data = response.text.replace('\r\n', '')
    province_data = re.findall('provinceObject = (.+?) return provinceObject', data)[0]
    province_data = json.loads(province_data.replace("'", '"'))

    for province_code in province_data.keys():
        province_url = 'https://moneymart.ca/storeLocatorService/stores/provinces?provinceId={}'.format(province_code)
        province_response = session.get(province_url)
        province_data = json.loads(province_response.text)
    
        for store_data in province_data:
            location_name = store_data['businessName']
            street_address = store_data['streetAddress1']
            if store_data['streetAddress2']:
                street_address += ', ' + store_data['streetAddress2']
            street_address = street_address if street_address else '<MISSING>'
            city = store_data['cityTown']
            city = city if city else '<MISSING>'
            state = store_data['stateProvinceId']
            state = state if state else '<MISSING>'
            zip_code = store_data['postCode']
            zip_code = zip_code if zip_code else '<MISSING>'
            country_code = store_data['countryId']
            country_code = country_code if country_code else '<MISSING>'
            store_number = store_data['storeNumber']
            phone = store_data['phone']
            phone = phone if phone else '<MISSING>'
            location_type = '<MISSING>'
            latitude = store_data['latitudeCoordinate']
            latitude = latitude if latitude else '<MISSING>'
            longitude = store_data['longitudeCoordinate']
            longitude = longitude if longitude else '<MISSING>'
            hours_of_operation = []
            for key, value in store_data.items():
                if 'Hours' in key:
                    hours_of_operation.append('{} - {}'.format(key.replace('Hours', ''), value))
            hours_of_operation = ', '.join(hours_of_operation) if hours_of_operation else '<MISSING>'
            store_url = 'https://www.moneymart.com/StoreDetails/StoreDetails?CA/{}/{}/{}/{}/{}'
            store_url = store_url.format(state, city.replace(' ', '-'), street_address.replace(' ', '-'), zip_code, store_number)
            
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
