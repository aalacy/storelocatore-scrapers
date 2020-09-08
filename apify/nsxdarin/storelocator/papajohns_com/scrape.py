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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://locations.papajohns.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://locations.papajohns.com/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            if lurl.count('/') > 5:
                locs.append(lurl)
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        store = ''
        name = ''
        add = ''
        city = ''
        zc = ''
        phone = ''
        website = 'papajohns.com'
        typ = 'Restaurant'
        country = 'US'
        if '/canada/' in loc:
            country = 'CA'
        hours = ''
        lat = ''
        lng = ''
        for line2 in lines:
            if '{"ids":' in line2:
                store = line2.split('{"ids":')[1].split(',')[0]
            if name == '' and '"LocationName-geo">' in line2:
                name = "Papa John's Pizza " + line2.split('"LocationName-geo">')[1].split('<')[0]
            if '<meta itemprop="streetAddress" content="' in line2:
                add = line2.split('<meta itemprop="streetAddress" content="')[1].split('"')[0]
                city = line2.split('address-city">')[1].split('<')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                phone = line2.split('data-ya-track="phone">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if hours == '' and 'data-day-of-week-end-index="' in line2:
                hours = 'Mon: ' + line2.split('content="Mo ')[1].split('"')[0]
                hours = hours + '; Tue: ' + line2.split('content="Tu ')[1].split('"')[0]
                hours = hours + '; Wed: ' + line2.split('content="We ')[1].split('"')[0]
                hours = hours + '; Thu: ' + line2.split('content="Th ')[1].split('"')[0]
                hours = hours + '; Fri: ' + line2.split('content="Fr ')[1].split('"')[0]
                hours = hours + '; Sat: ' + line2.split('content="Sa ')[1].split('"')[0]
                hours = hours + '; Sun: ' + line2.split('content="Su ')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
