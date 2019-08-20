import csv
import urllib2
import requests
import sgzip
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for code in sgzip.for_radius(50):
        print('Pulling Zip Code %s...' % code)
        url = 'https://boostmobile.nearestoutlet.com/cgi-bin/jsonsearch-cs.pl?showCaseInd=false&brandId=bst&results=50&zipcode=' + code + '&page=1'
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        rc = 0
        for item in array['nearestOutletResponse']['nearestlocationinfolist']['nearestLocationInfo']:
            website = 'boostmobile.com'
            store = item['id']
            name = 'Boost Mobile'
            typ = item['storeName']
            add = item['storeAddress']['primaryAddressLine']
            city = item['storeAddress']['city']
            state = item['storeAddress']['state']
            zc = item['storeAddress']['zipCode']
            lat = item['storeAddress']['lat']
            lng = item['storeAddress']['long']
            country = 'US'
            phone = item['storePhone']
            hours = 'Mon: ' + item['storeHours']['mon']
            hours = hours + '; Tue: ' + item['storeHours']['tue']
            hours = hours + '; Wed: ' + item['storeHours']['wed']
            hours = hours + '; Thu: ' + item['storeHours']['thu']
            hours = hours + '; Fri: ' + item['storeHours']['fri']
            hours = hours + '; Sat: ' + item['storeHours']['sat']
            hours = hours + '; Sun: ' + item['storeHours']['sun']
            if lat == '':
                lat = '<MISSING>'
            if lng == '':
                lng = '<MISSING>'
            if phone == '':
                phone = '<MISSING>'
            if 'see store' in hours.lower():
                hours = '<MISSING>'
            if store not in ids and store != '':
                ids.append(store)
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
