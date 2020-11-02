import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
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
    locs = []
    url = 'https://www.topman.com/api/store-locator?country=United+States&brand=12555&cfsi=true'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item['storeId']
        website = 'us.topman.com'
        typ = item['brandName']
        name = item['name']
        country = 'US'
        add = item['address']['line1']
        city = item['address']['city']
        if city == '0':
            city = 'Washington'
            state = 'DC'
            add = item['address']['line1'].split(',')[1].strip()
        else:
            state = '<MISSING>'
        zc = item['address']['postcode']
        add = add + ' ' + item['address']['line2'].strip()
        add = add.strip()
        if zc == '':
            zc = '<MISSING>'
        phone = item['telephoneNumber'].replace('(+001) ','')
        if phone == '':
            phone = '<MISSING>'
        hours = 'Mon: ' + item['openingHours']['monday']
        hours = hours + '; Tue: ' + item['openingHours']['tuesday']
        hours = hours + '; Wed: ' + item['openingHours']['wednesday']
        hours = hours + '; Thu: ' + item['openingHours']['thursday']
        hours = hours + '; Fri: ' + item['openingHours']['friday']
        hours = hours + '; Sat: ' + item['openingHours']['saturday']
        hours = hours + '; Sun: ' + item['openingHours']['sunday']
        if '-' not in hours:
            hours = '<MISSING>'
        if 'Cedar Rapids' in name:
            city = 'Cedar Rapids'
        lat = '<MISSING>'
        lng = '<MISSING>'
        loc = '<MISSING>'
        if 'Nordstrom 808' in add:
            add = '7700 18th St SW'
        if 'Nordstrom ' in add:
            add = add.split(' ',1)[1]
            try:
                add = add.split(' ',1)[1]
            except:
                add = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
