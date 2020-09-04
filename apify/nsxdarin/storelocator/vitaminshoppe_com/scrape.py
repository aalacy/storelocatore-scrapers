import json
import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import gzip
import os

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
    states = []
    cities = []
    url = 'https://locations.vitaminshoppe.com'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'title="Stores in ' in line and '{{url' not in line:
            states.append(line.split('href="')[1].split('"')[0])
    for state in states:
        print(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'title="Stores in ' in line2 and '<a href="https://locations.vitaminshoppe.com/' in line2:
                cities.append(line2.split('href="')[1].split('"')[0])
    for city in cities:
        print(('Pulling City %s...' % city))
        r2 = session.get(city, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'data-show-country="en-ca" data-gaq="Maplist, Location Link' in line2 and '<a href="https://locations.vitaminshoppe.com/' in line2:
                lurl = line2.split('href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        PFound = True
        while PFound:
            try:
                PFound = False
                r2 = session.get(loc, headers=headers)
                if r2.encoding is None: r2.encoding = 'utf-8'
                print(('Pulling Location %s...' % loc))
                website = 'vitaminshoppe.com'
                name = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                country = 'US'
                store = loc.rsplit('-',1)[1].split('.')[0]
                phone = ''
                lat = ''
                lng = ''
                typ = '<MISSING>'
                hours = ''
                lines = r2.iter_lines(decode_unicode=True)
                for line2 in lines:
                    if '<h2 class="mt-20 mb-20">' in line2:
                        name = line2.split('<h2 class="mt-20 mb-20">')[1].split('<')[0]
                    if '"streetAddress": "' in line2:
                        add = line2.split('"streetAddress": "')[1].split('"')[0]
                    if '"addressLocality": "' in line2:
                        city = line2.split('"addressLocality": "')[1].split('"')[0]
                    if '"addressRegion": "' in line2:
                        state = line2.split('"addressRegion": "')[1].split('"')[0]
                    if '"postalCode": "' in line2:
                        zc = line2.split('"postalCode": "')[1].split('"')[0]
                    if '"telephone": "' in line2:
                        phone = line2.split('"telephone": "')[1].split('"')[0]
                    if '"latitude": "' in line2:
                        lat = line2.split('latitude": "')[1].split('"')[0]
                    if '"longitude": "' in line2:
                        lng = line2.split('longitude": "')[1].split('"')[0]
                    if '"openingHours": "' in line2:
                        hours = line2.split('"openingHours": "')[1].split('"')[0]
                if name != '':
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                PFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
