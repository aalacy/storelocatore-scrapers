import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    states = []
    cities = []
    locs = []
    url = 'https://stores.libertytravel.com/index.html'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'c-directory-list-content-item-link" href="' in line:
            items = line.split('c-directory-list-content-item-link" href="')
            for item in items:
                if 'item-count">(' in item:
                    count = item.split('item-count">(')[1].split(')')[0]
                    if count == '1':
                        locs.append('https://stores.libertytravel.com/' + item.split('"')[0])
                    else:
                        states.append('https://stores.libertytravel.com/' + item.split('"')[0])
    for state in states:
        print('Pulling State %s...' % state)
        rs = session.get(state, headers=headers)
        for line2 in rs.iter_lines():
            if '<a class="c-directory-list-content-item-link" href="' in line2:
                items = line2.split('<a class="c-directory-list-content-item-link" href="')
                for item in items:
                    if 'item-count">(' in item:
                        count = item.split('item-count">(')[1].split(')')[0]
                        if count == '1':
                            locs.append('https://stores.libertytravel.com/' + item.split('"')[0])
                        else:
                            cities.append('https://stores.libertytravel.com/' + item.split('"')[0])
    for city in cities:
        print('Pulling City %s...' % city)
        rs = session.get(city, headers=headers)
        for line2 in rs.iter_lines():
            if '<a class="Link" data-ya-track="view_page" href="..' in line2:
                items = line2.split('<a class="Link" data-ya-track="view_page" href="..')
                for item in items:
                    if '>View Page</a>' in item:
                        locs.append('https://stores.libertytravel.com/' + item.split('"')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        rs = session.get(loc, headers=headers)
        website = 'libertytravel.com'
        name = '<MISSING>'
        add = '<MISSING>'
        city = '<MISSING>'
        state = '<MISSING>'
        zc = '<MISSING>'
        phone = '<MISSING>'
        hours = '<MISSING>'
        country = 'US'
        typ = '<MISSING>'
        store = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        for line2 in rs.iter_lines():
            if ',"id":' in line2:
                typ = line2.split('"name":"')[1].split('"')[0]
                store = line2.split(',"id":')[1].split(',')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split(',')[0]
            if 'Heading--1 Heading--geomod">' in line2:
                name = line2.split('Heading--1 Heading--geomod">')[1].split('<')[0]
                hrs = line2.split('itemprop="openingHours" content="')
                for hr in hrs:
                    if '<span class="c-location-hours-today-day-status">' in hr:
                        if hours == '':
                            hours = hr.split('"')[0]
                        else:
                            hours = hours + '; ' + hr.split('"')[0]
                add = line2.split('<meta itemprop="streetAddress" content="')[1].split('"')[0]
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                phone = line2.split('data-ya-track="nap_phone_call">')[1].split('<')[0]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
