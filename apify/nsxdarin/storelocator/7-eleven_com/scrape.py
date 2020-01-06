import csv
import urllib2
from requests.exceptions import ConnectionError
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
    states = []
    url = 'https://www.7-eleven.com/locations'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<li><a href="/locations/' in line:
            items = line.split('<li><a href="/locations/')
            for item in items:
                if 'All Stores' not in item:
                    states.append('https://www.7-eleven.com/locations/' + item.split('"')[0])
    for state in states:
        cities = []
        locs = []
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<li><a href="/locations/' in line:
                items = line2.split('<li><a href="/locations/')
                for item in items:
                    if 'class="locations-list">' not in item:
                        cities.append('https://www.7-eleven.com/locations/' + item.split('"')[0])
        for city in cities:
            print('Pulling City %s...' % city)
            r3 = session.get(city, headers=headers)
            for line3 in r3.iter_lines():
                if 'class="se-amenities se-local-store" href="/locations/' in line3:
                    items = line3.split('class="se-amenities se-local-store" href="/locations/')
                    for item in items:
                        if '<!DOCTYPE html>' not in item:
                            locs.append('https://www.7-eleven.com/locations/' + item.split('"')[0])
        for loc in locs:
            print('Pulling Location %s...' % loc)
            website = '7-eleven.com'
            typ = ''
            name = '7-Eleven'
            hours = ''
            phone = ''
            store = ''
            city = ''
            add = ''
            state = ''
            zc = ''
            lat = ''
            lng = ''
            country = 'US'
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '"hours":{"message":"' in line2:
                    hours = line2.split('"hours":{"message":"')[1].split('"')[0]
                if '"localStoreLatLon":{"lat":' in line2:
                    lat = line2.split('"localStoreLatLon":{"lat":')[1].split(',')[0]
                    lng = line2.split(',"lon":')[1].split('}')[0]
                if '"currentStoreID":' in line2:
                    store = line2.split('"currentStoreID":')[1].split(',')[0]
                if '<div class="background-gradient"></div><h5>' in line2:
                    typ = line2.split('<div class="background-gradient"></div><h5>')[1].split('<')[0]
                if '"localStoreData":{"currentStore":' in line2:
                    phone = line2.split('"localStoreData":{"currentStore":')[1].split('"phone":"')[1].split('"')[0]
                    add = line2.split('"localStoreData":{"currentStore":')[1].split('"address":"')[1].split('"')[0]
                    zc = line2.split('"localStoreData":{"currentStore":')[1].split('"zip":"')[1].split('"')[0]
                    state = line2.split('"localStoreData":{"currentStore":')[1].split('"state":"')[1].split('"')[0]
                    city = line2.split('"localStoreData":{"currentStore":')[1].split('"city":"')[1].split('"')[0]
            if hours == '':
                hours = '<MISSING>'
            if phone == '':
                phone = '<MISSING>'
            if '00000000' not in phone and add != '':
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
