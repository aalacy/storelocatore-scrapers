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
    url = 'https://www.journeys.ca/stores'
    states = []
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<option value="' in line and '<option value=""' not in line and 'miles' not in line:
            states.append(line.split('<option value="')[1].split('"')[0])
    for state in states:
        print(('Pulling Province %s...' % state))
        findurl = 'https://www.journeys.ca/stores?StateOrProvince=' + state + '&PostalCode=&MileRadius=&Latitude=&Longitude=&Mode=search'
        r2 = session.get(findurl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'class="store-name">' in line2:
                surl = 'https://www.journeys.ca' + line2.split('href="')[1].split('"')[0]
                if surl not in locs:
                    locs.append(surl)
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        AFound = False
        lines = r2.iter_lines(decode_unicode=True)
        website = 'journeys.ca'
        add = ''
        hours = ''
        for line2 in lines:
            if '<p itemprop="streetAddress">' in line2:
                AFound = True
            if AFound and '<span itemprop="addressLocality">' in line2:
                website = 'journeys.ca'
                AFound = False
                typ = 'Store'
                city = line2.split('span itemprop="addressLocality">')[1].split('<')[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('"postalCode">')[1].split('<')[0]
                country = 'CA'
            if AFound and '<p item' not in line2 and '</p>' in line2 and '<p>' in line2:
                add = add + ' ' + line2.split('<p>')[1].split('<')[0]
            if "Store ID', '" in line2:
                store = line2.split("Store ID', '")[1].split("'")[0]
                name = 'Journeys Store #' + store
            if '<span itemprop="telephone">' in line2:
                phone = line2.split('<span itemprop="telephone">')[1].split('<')[0]
            if '<span itemprop="openingHours"' in line2:
                hrs = line2.split('<span itemprop="openingHours"')[1].split('">')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '</html>' in line2:
                lat = '<MISSING>'
                lng = '<MISSING>'
        add = add.strip()
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
