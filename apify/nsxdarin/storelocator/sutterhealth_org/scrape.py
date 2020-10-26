# -*- coding: utf-8 -*-
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
    alllocs = []
    types = ['birth-centers',
             'care-centers',
             'emergency-rooms',
             'home-health-hospice',
             'hospitals',
             'imaging',
             'integrative-health-healing',
             'labs',
             'libraries-resource-centers',
             'occupational-health',
             'physical-therapy-rehab',
             'surgery-centers',
             'transplant-outreach-clinics',
             'urgent-care',
             'walk-in-care'
             ]
    for htyp in types:
        locs = []
        url = 'https://www.sutterhealth.org/location-search?location-type=' + htyp + '&location-city=&location-affiliate=&location-lat=&location-lng=&location-distance=8.07&location-service=&location-auto=&sort-type=&q=&start=1&max=250'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<div class="location__media"><a href="' in line:
                lurl = 'https://www.sutterhealth.org' + line.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    locs.append(lurl)
        for loc in locs:
            print(('Pulling Location %s...' % loc))
            website = 'sutterhealth.org'
            typ = htyp
            hours = ''
            name = ''
            add = ''
            city = ''
            state = ''
            zc = ''
            country = 'US'
            store = '<MISSING>'
            phone = ''
            lat = ''
            lng = ''
            r2 = session.get(loc, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<title>' in line2:
                    name = line2.split('<title>')[1].split(' |')[0]
                if 'itemprop="streetAddress">' in line2:
                    add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
                if '<span itemprop="addressLocality">' in line2:
                    city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
                if '<span itemprop="addressRegion">' in line2:
                    state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                if '<span itemprop="postalCode">' in line2:
                    zc = line2.split('<span itemprop="postalCode">')[1].split('<')[0]
                    if 'phone"><span content="' in line2:
                        phone = line2.split('phone"><span content="')[1].split('"')[0]
                    else:
                        phone = '<MISSING>'
                if '<meta itemprop="latitude" content="' in line2:
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                if '<meta itemprop="longitude" content="' in line2:
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                if '"detail-block--days">' in line2 and 'Holidays</div>' not in line2:
                    hrs = line2.split('"detail-block--days">')[1].split('<')[0]
                if 'Holidays</div>' in line2 or 'Other<' in line2:
                    hrs = 'XXX'
                if '"detail-block--hours">' in line2 and hrs != 'XXX':
                    hrs = hrs + ': ' + line2.split('"detail-block--hours">')[1].split('</div')[0].replace('<br />',', ')
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
                    hours = hours.replace('–','-')
                    hours = hours.replace(' ',' ')
            if hours == '':
                hours = '<MISSING>'
            if '-' not in hours:
                hours = '<MISSING>'
            hours = hours.replace(' – ',' - ').replace(' ',' ')
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
