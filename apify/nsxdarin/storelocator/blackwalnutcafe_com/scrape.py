# -*- coding: cp1252 -*-
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
    locs = []
    url = 'https://www.blackwalnutcafe.com/locations/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<p class="address">' in line:
            zcode = line.split('<p class="address">')[1].split('<')[0].rsplit(' ',1)[1]
        if 'See Location Details</a>' in line:
            locs.append(line.split('href="')[1].split('"')[0] + '|' + zcode)
    for loc in locs:
        print(('Pulling Location %s...' % loc.split('|')[0]))
        website = 'blackwalnutcafe.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        country = 'US'
        lat = '<MISSING>'
        lng = '<MISSING>'
        store = '<MISSING>'
        phone = ''
        zc = loc.split('|')[1]
        r2 = session.get(loc.split('|')[0], headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' - ')[0]
            if '<h2>Location Information</h2>' in line2:
                g = next(lines)
                h = next(lines)
                i = next(lines)
                add2 = ''
                if ', ' not in h:
                    add2 = h.split('<')[0]
                    h = i
                    i = next(lines)
                phone = i.split('<')[0]
                add = g.split('>')[1].split('<')[0] + ' ' + add2
                add = add.strip()
                city = h.split(',')[0]
                state = h.split(',')[1].strip().split(' ')[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'day:' in line2:
                hrs = line2.replace('\t','').replace('\n','').replace('\r','').strip().replace('<p>','').replace('<br />','').replace('</p>','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        hours = hours.replace(' – ','-')
        hours = hours.replace('&#8211;','-')
        yield [website, loc.split('|')[0], name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
