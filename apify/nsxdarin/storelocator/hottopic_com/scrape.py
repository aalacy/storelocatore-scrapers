import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    url = 'https://www.hottopic.com/on/demandware.store/Sites-hottopic-Site/default/Stores-GetNearestStores?postalCode=10002&customStateCode=&maxdistance=10000&unit=mi&latitude=44.9479791&longitude=-93.29357779999998&maxResults=15000&distanceUnit=mi&countryCode=US'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if ': {' in line and '{"stores":' not in line and '"image"' not in line:
            store = line.split('"')[1]
        if '"name": "' in line:
            name = line.split('"name": "')[1].split('"')[0]
        if '"address1": "' in line:
            add = line.split('"address1": "')[1].split('"')[0]
        if '"address2": "' in line:
            add = add + ' ' + line.split('"address2": "')[1].split('"')[0]
            add = add.strip()
        if '"postalCode": "' in line:
            zc = line.split('"postalCode": "')[1].split('"')[0]
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
        if '"stateCode": "' in line:
            state = line.split('"stateCode": "')[1].split('"')[0]
        if '"countryCode": "' in line:
            country = line.split('"countryCode": "')[1].split('"')[0]
        if '"phone": "' in line:
            phone = line.split('"phone": "')[1].split('"')[0]
        if '"latitude": "' in line:
            lat = line.split('"latitude": "')[1].split('"')[0]
        if '"longitude": "' in line:
            lng = line.split('"longitude": "')[1].split('"')[0]
            hours = '<MISSING>'
            website = 'hottopic.com'
            typ = 'Store'
            if phone == '':
                phone = '<MISSING>'
            if ' ' in zc:
                country = 'CA'
            purl = '<MISSING>'
            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
