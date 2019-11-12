import csv
import urllib2
import requests
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
    canada = ['Yukon','British','Sask','Alberta','Ontario','Prince Edward','Manitoba','Quebec','Newfoundland','Nova Scotia','New Brunswick']
    url = 'https://locations.panerabread.com/index.html'
    states = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="c-directory-list-content-item-link" href="' in line:
            items = line.split('<a class="c-directory-list-content-item-link" href="')
            for item in items:
                if '<!doctype html>' not in item:
                    place = item.split('">')[1].split('<')[0]
                    if place in canada:
                        states.append('https://locations.panerabread.com/' + item.split('"')[0])
    cities = []
    locs = []
    for state in states:
        print('Pulling Province %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<a class="c-directory-list-content-item-link" href="' in line2:
                items = line2.split('<a class="c-directory-list-content-item-link" href="')
                for item in items:
                    if '<!doctype' not in item:
                        lurl = 'https://locations.panerabread.com/' + item.split('"')[0]
                        if lurl.count('/') == 5:
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if 'aria-level="2"><a href="../' in line2:
                items = line2.split('aria-level="2"><a href="../')
                for item in items:
                    if '<!doctype' not in item:
                        lurl = 'https://locations.panerabread.com/' + item.split('"')[0]
                        locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
        name = ''
        typ = 'Restaurant'
        website = 'panera.ca'
        add = ''
        city = ''
        state = ''
        country = 'CA'
        zc = ''
        hours = ''
        lat = ''
        lng = ''
        store = ''
        phone = ''
        for line2 in r2.iter_lines():
            if '<span class="location-name-geo">' in line2:
                name = line2.split('<span class="location-name-geo">')[1].split('<')[0].strip()
            if '"c-address-street-1">' in line2:
                add = line2.split('"c-address-street-1">')[1].split('<')[0].strip()
                addinfo = line2.split('<span class="c-address-street-1">')[1].split('<span class="c-address-city">')[0]
                if 'class="c-address-street-2">' in addinfo:
                    add = add + ' ' + line2.split('class="c-address-street-2">')[1].split('<')[0].strip()
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0].strip()
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0].strip()
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
            if 'data-ya-track="phonecall">' in line2:
                phone = line2.split('data-ya-track="phonecall">')[1].split('<')[0].strip()
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if '{"ids":' in line2:
                store = line2.split('{"ids":')[1].split(',')[0]
            if "data-days='[" in line2:
                days = line2.split("data-days='[")[1].split("]}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals"' in day:
                        if hours == '':
                            hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        else:
                            hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
