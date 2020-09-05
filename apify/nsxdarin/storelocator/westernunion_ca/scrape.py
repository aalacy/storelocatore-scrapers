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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    for x in range(1, 15):
        print(('Pulling Sitemap %s...' % str(x)))
        smurl = 'http://locations.westernunion.com/sitemap-' + str(x) + '.xml.gz'
        with open('branches.xml.gz','wb') as f:
            f.write(urllib.request.urlopen(smurl).read())
            f.close()
            with gzip.open('branches.xml.gz', 'rb') as f:
                for line in f:
                    if '<loc>http://locations.westernunion.com/ca/' in line:
                        locs.append(line.split('<loc>')[1].split('<')[0])
        print((str(len(locs)) + ' Locations Found...'))
    for loc in locs:
        website = 'westernunion.ca'
        typ = 'Location'
        store = '<MISSING>'
        hours = '<MISSING>'
        city = ''
        add = ''
        state = ''
        zc = ''
        if '/us/' in loc:
            country = 'US'
        if '/ca/' in loc:
            country = 'CA'
        name = ''
        phone = ''
        lat = ''
        lng = ''
        r = session.get(loc, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        lines = r.iter_lines(decode_unicode=True)
        AFound = False
        for line in lines:
            if '<h1 class="offscreen">' in line:
                name = line.split('<h1 class="offscreen">')[1].split('<')[0]
                if 'Western Union Agent Location' in name:
                    name = name.replace(name[:32], '')
                    name = name.strip()
            if 'itemprop="streetAddress">' in line and AFound is False:
                AFound = True
                add = line.split('itemprop="streetAddress">')[1].split('<')[0]
            if 'itemprop="addressLocality">' in line:
                city = line.split('itemprop="addressLocality">')[1].split('<')[0]
            if 'itemprop="addressRegion">' in line:
                state = line.split('itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="postalCode">' in line:
                zc = line.split('itemprop="postalCode">')[1].split('<')[0]
            if 'aria-label="Telephone">' in line:
                phone = line.split('aria-label="Telephone">')[1].split('<')[0]
            if 'itemprop="latitude" content="' in line:
                lat = line.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line:
                lng = line.split('itemprop="longitude" content="')[1].split('"')[0]
            if '"id":"' in line:
                store = line.split('"id":"')[1].split('"')[0]
            if '<meta itemprop="openingHours" content="' in line:
                if hours == '<MISSING>':
                    hours = line.split('<meta itemprop="openingHours" content="')[1].split('"')[0]
                else:
                    hours = hours + '; ' + line.split('<meta itemprop="openingHours" content="')[1].split('"')[0]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
