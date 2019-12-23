import csv
import urllib2
import requests
import json
from sgzip import sgzip


session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=50&lat=' + str(x) + '&long=' + str(y)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '"ID": "' in line:
                hours = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                country = 'US'
                typ = '<MISSING>'
                lat = ''
                lng = ''
                phone = ''
                website = 'sallybeauty.com'
                store = line.split('"ID": "')[1].split('"')[0]
            if '"name": "' in line:
                name = line.split('"name": "')[1].split('"')[0]
            if '"address1": "' in line:
                add = line.split('"address1": "')[1].split('"')[0]
            if '"address2": "' in line:
                add = add + ' ' + line.split('"address2": "')[1].split('"')[0]
                add = add.strip()
            if '"city": "' in line:
                city = line.split('"city": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": "' in line:
                lat = line.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line:
                lng = line.split('"longitude": "')[1].split('"')[0]
            if '"phone": "' in line:
                phone = line.split('"phone": "')[1].split('"')[0]
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
            if '"storeHours": "' in line:
                hours = 'Monday:' + line.split("<div class='store-hours-day'>Monday:")[1].split('</span></div>\\n        </div>')[0]
                hours = hours.replace('</span></div>','; ')
                hours = hours.replace('<span class=\\"hours-of-day\\">','').replace('</span>','').replace('</div>','').replace('\\n            ','')
                hours = hours.replace("<div class='store-hours-day'>",'').replace('closed - closed','closed')
                if store not in ids:
                    ids.append(store)
                    print('Pulling Store ID #%s...' % store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
