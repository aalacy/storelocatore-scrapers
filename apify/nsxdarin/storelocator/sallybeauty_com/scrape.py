import csv
import urllib.request, urllib.error, urllib.parse
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
    canadaurls = ['https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Winnipeg%2C%20AB&radius=300',
                  'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Vancouver%2C%20BC&radius=300',
                  'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Montreal%2C%20QC&radius=300',
                  'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=St.%20John%27s%2C%20NL&radius=300',
                  'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Calgary%2C%20AB&radius=300',
                  'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=300&postalCode=Toronto%2C%20ON&radius=300'
                  ]
    for curl in canadaurls:
        url = curl
        print(('Pulling Canada URL %s...' % curl))
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ''
                loc = '<MISSING>'
                add = ''
                city = ''
                state = ''
                zc = ''
                country = ''
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
                cas = ['AB','BC','MB','NL','ON','NB','QC','PQ','SK','PE','PEI']
                if state in cas:
                    country = 'CA'
                if store not in ids and country == 'CA':
                    ids.append(store)
                    print(('Pulling Store ID #%s...' % store))
                    hours = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        print(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        url = 'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=50&lat=' + str(x) + '&long=' + str(y)
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ''
                loc = '<MISSING>'
                add = ''
                city = ''
                state = ''
                zc = ''
                country = ''
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
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                if store not in ids and ' ' not in zc:
                    ids.append(store)
                    print(('Pulling Store ID #%s...' % store))
                    hours = '<MISSING>'
                    country = 'US'
                    if zc == '':
                        zc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        x = float(float(coord[0]) - 0.25)
        y = float(float(coord[1]) - 0.25)
        print(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        url = 'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=50&lat=' + str(x) + '&long=' + str(y)
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ''
                loc = '<MISSING>'
                add = ''
                city = ''
                state = ''
                zc = ''
                country = ''
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
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                if store not in ids and ' ' not in zc:
                    ids.append(store)
                    print(('Pulling Store ID #%s...' % store))
                    hours = '<MISSING>'
                    country = 'US'
                    if zc == '':
                        zc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        x = float(float(coord[0]) + 0.25)
        y = float(float(coord[1]) + 0.25)
        print(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        url = 'https://www.sallybeauty.com/on/demandware.store/Sites-SA-Site/default/Stores-FindStores?showMap=true&radius=50&lat=' + str(x) + '&long=' + str(y)
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"ID": "' in line:
                hours = ''
                loc = '<MISSING>'
                add = ''
                city = ''
                state = ''
                zc = ''
                country = ''
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
            if '"stateCode": "' in line:
                state = line.split('"stateCode": "')[1].split('"')[0]
                if store not in ids and ' ' not in zc:
                    ids.append(store)
                    print(('Pulling Store ID #%s...' % store))
                    hours = '<MISSING>'
                    country = 'US'
                    if zc == '':
                        zc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
