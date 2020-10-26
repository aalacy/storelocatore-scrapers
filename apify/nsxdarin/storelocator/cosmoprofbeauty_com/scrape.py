import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import gzip
import os
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cosmoprofbeauty_com')



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
    canada = ['AB','BC','MB','NB','NL','NS','ON','PE','SK','QC']
    for x in range(1, 5):
        #logger.info(('Pulling Sitemap %s...' % str(x)))
        smurl = 'https://stores.cosmoprofbeauty.com/sitemap/sitemap' + str(x) + '.xml.gz'
        with open('branches.xml.gz','wb') as f:
            f.write(urllib.request.urlopen(smurl).read())
            f.close()
            with gzip.open('branches.xml.gz', 'rt') as f:
                for line in f:
                    if '<loc>https://stores.cosmoprofbeauty.com/' in line and '.html' in line:
                        locs.append(line.split('<loc>')[1].split('<')[0])
        #logger.info((str(len(locs)) + ' Locations Found...'))
    for loc in locs:
        website = 'cosmoprofbeauty.com'
        typ = '<MISSING>'
        add = ''
        store = ''
        name = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        hours = ''
        lat = ''
        lng = ''
        r = session.get(loc, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        lines = r.iter_lines(decode_unicode=True)
        for line in lines:
            if '<div class="map-list-item-wrap" data-fid="' in line:
                store = line.split('<div class="map-list-item-wrap" data-fid="')[1].split('"')[0]
                name = 'CosmoProf #' + store
            if '"address_1\\": \\"' in line:
                add = line.split('"address_1\\": \\"')[1].split('\\')[0] + ' ' + line.split('"address_2\\": \\"')[1].split('\\')[0]
                add = add.strip()
                city = line.split('"city\\": \\"')[1].split('\\')[0]
                state = line.split('"region\\": \\"')[1].split('\\')[0]
                zc = line.split('"post_code\\": \\"')[1].split('\\')[0]
                lat = line.split('"lat\\": \\"')[1].split('\\')[0]
                lng = line.split('"lng\\": \\"')[1].split('\\')[0]
                loc = line.split('"url\\": \\"')[1].split('\\')[0]
            if '"telephone": "' in line:
                phone = line.split('"telephone": "')[1].split('"')[0]
            if '"openingHours": "' in line:
                hours = line.split('"openingHours": "')[1].split('"')[0]
        if state in canada:
            country = 'CA'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if '6841' in phone and state == 'PR':
            add = 'Los Jardines S/C Rd #20'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
