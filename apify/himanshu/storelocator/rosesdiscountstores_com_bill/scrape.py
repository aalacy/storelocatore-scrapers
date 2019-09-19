import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    return_main_object = []
    base_url = "https://www.rosesdiscountstores.com/"
    zips = sgzip.for_radius(100)
    addresses= []


    r = requests.get("https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=82.292272%2C90.108768&southwest=-57.393433%2C-180").json()

    for vj in r['locations']:


        locator_domain = base_url

        location_name = vj['name']
        street_address = vj['address1'].strip()
        vk = vj['address'].split(',')[2].strip().split(' ')[0].strip()

        city = vj['city'].strip()
        state = vk
        zip = vj['postcode'].strip()

        store_number = vj['id']
        country_code = vj['countryCode'].strip()

        phone = ''

        location_type = 'rosesdiscountstores'
        latitude = vj['lat']
        longitude = vj['lng']

        if street_address in addresses:
            continue
        addresses.append(street_address)

        hours_of_operation = ''
        if 'hoursOfOperation' in   vj['hours']:
            hours_of_operation = ' mon ' + vj['hours']['hoursOfOperation']['mon'] + ' tue ' + vj['hours']['hoursOfOperation']['tue'] + ' thu ' + vj['hours']['hoursOfOperation']['thu'] + ' fri ' + vj['hours']['hoursOfOperation']['fri'] + ' sat ' + vj['hours']['hoursOfOperation']['sat'] + ' sun ' + vj['hours']['hoursOfOperation']['sun']

        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        print('===', str(store))

        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
