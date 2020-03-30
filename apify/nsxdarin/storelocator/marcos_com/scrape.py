import csv
import urllib2
from sgrequests import SgRequests
import sgzip
import time
import json

session = SgRequests()
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
    puertourl = 'https://www.marcos.com/api/stores/searchByStreetAddress?orderType=Pickup&street=&city=Guayama&state=PR&zip=&radius=100&country=US'
    r = session.get(puertourl, headers=headers)
    if '"results":' in r.content:
        for item in json.loads(r.content)['results']:
            name = item['name']
            if '#' in name:
                store = name.split('#')[1]
            else:
                store = '<MISSING>'
            try:
                loc = item['baseUrl']
            except:
                loc = '<MISSING>'
            if 'store' in loc:
                store = loc.split('store')[1].split('.')[0]
            lat = item['lat']
            lng = item['lng']
            add = item['address']
            country = 'US'
            try:
                phone = item['telephone']
            except:
                phone = '<MISSING>'
            typ = 'Restaurant'
            status = item['status']
            state = item['state']
            zc = item['zip']
            city = item['city']
            website = 'marcos.com'
            try:
                hours = 'Sun: ' + item['storeHours']['any'][0]['openTime'] + '-' + item['storeHours']['any'][0]['closeTime']
            except:
                hours = 'Sun: Closed'
            try:
                hours = hours + '; Mon: ' + item['storeHours']['any'][1]['openTime'] + '-' + item['storeHours']['any'][1]['closeTime']
            except:
                hours = hours + '; Mon: Closed'
            try:
                hours = hours + '; Tue: ' + item['storeHours']['any'][2]['openTime'] + '-' + item['storeHours']['any'][2]['closeTime']
            except:
                hours = hours + '; Tue: Closed'
            try:
                hours = hours + '; Wed: ' + item['storeHours']['any'][3]['openTime'] + '-' + item['storeHours']['any'][3]['closeTime']
            except:
                hours = hours + '; Wed: Closed'
            try:
                hours = hours + '; Thu: ' + item['storeHours']['any'][4]['openTime'] + '-' + item['storeHours']['any'][4]['closeTime']
            except:
                hours = hours + '; Thu: Closed'
            try:
                hours = hours + '; Fri: ' + item['storeHours']['any'][5]['openTime'] + '-' + item['storeHours']['any'][5]['closeTime']
            except:
                hours = hours + '; Fri: Closed'
            try:
                hours = hours + '; Fri: ' + item['storeHours']['any'][6]['openTime'] + '-' + item['storeHours']['any'][6]['closeTime']
            except:
                hours = hours + '; Fri: Closed'
            if store == '<MISSING>':
                store = name.split(' -')[0]
            if name not in ids and status == 'Live':
                ids.append(name)
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    for code in sgzip.for_radius(100):
        print('Pulling Zip Code %s...' % code)
        url = 'https://www.marcos.com/api/stores/searchByStreetAddress?orderType=Pickup&street=&city=&state=&zip=' + code + '&radius=100&country=US'
        r = session.get(url, headers=headers)
        if '"results":' in r.content:
            for item in json.loads(r.content)['results']:
                name = item['name']
                if '#' in name:
                    store = name.split('#')[1]
                else:
                    store = '<MISSING>'
                try:
                    loc = item['baseUrl']
                except:
                    loc = '<MISSING>'
                if 'store' in loc:
                    store = loc.split('store')[1].split('.')[0]
                lat = item['lat']
                lng = item['lng']
                add = item['address']
                country = 'US'
                try:
                    phone = item['telephone']
                except:
                    phone = '<MISSING>'
                typ = 'Restaurant'
                status = item['status']
                state = item['state']
                zc = item['zip']
                city = item['city']
                website = 'marcos.com'
                try:
                    hours = 'Sun: ' + item['storeHours']['any'][0]['openTime'] + '-' + item['storeHours']['any'][0]['closeTime']
                except:
                    hours = 'Sun: Closed'
                try:
                    hours = hours + '; Mon: ' + item['storeHours']['any'][1]['openTime'] + '-' + item['storeHours']['any'][1]['closeTime']
                except:
                    hours = hours + '; Mon: Closed'
                try:
                    hours = hours + '; Tue: ' + item['storeHours']['any'][2]['openTime'] + '-' + item['storeHours']['any'][2]['closeTime']
                except:
                    hours = hours + '; Tue: Closed'
                try:
                    hours = hours + '; Wed: ' + item['storeHours']['any'][3]['openTime'] + '-' + item['storeHours']['any'][3]['closeTime']
                except:
                    hours = hours + '; Wed: Closed'
                try:
                    hours = hours + '; Thu: ' + item['storeHours']['any'][4]['openTime'] + '-' + item['storeHours']['any'][4]['closeTime']
                except:
                    hours = hours + '; Thu: Closed'
                try:
                    hours = hours + '; Fri: ' + item['storeHours']['any'][5]['openTime'] + '-' + item['storeHours']['any'][5]['closeTime']
                except:
                    hours = hours + '; Fri: Closed'
                try:
                    hours = hours + '; Fri: ' + item['storeHours']['any'][6]['openTime'] + '-' + item['storeHours']['any'][6]['closeTime']
                except:
                    hours = hours + '; Fri: Closed'
                if store == '<MISSING>':
                    store = name.split(' -')[0]
                if name not in ids and status == 'Live':
                    ids.append(name)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
