import csv
import urllib.request, urllib.error, urllib.parse
import requests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tacobell_ca')



session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.tacobell.ca/en/stores/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<script id="all_stores_locations"' in line:
            items = line.split('"slug": "')
            for item in items:
                if '<script id="all_stores_locations"' not in item:
                    sid = item.split('"')[0]
                    lat = item.split('"latitude": ')[1].split(',')[0]
                    lng = item.split('"longitude": ')[1].split(',')[0]
                    lurl = 'https://www.tacobell.ca/en/store/' + sid
                    locs.append(lurl + '|' + lat + '|' + lng)
    
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc.split('|')[0]))
        website = 'tacobell.ca'
        typ = 'Restaurant'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'CA'
        store = '<MISSING>'
        phone = ''
        hours = ''
        lat = loc.split('|')[1]
        lng = loc.split('|')[2]
        name = 'Taco Bell'
        r2 = session.get(loc.split('|')[0], headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<h1 class="store-location-title">' in line2:
                add = line2.split('<h1 class="store-location-title">')[1].split('<')[0]
                g = next(lines)
                csz = g.split('>')[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip()
                zc = '<MISSING>'
                g = next(lines)
                phone = g.split('>')[1].split('<')[0]
            if 'day</td>' in line2:
                g = next(lines)
                h = next(lines)
                hrs = line2.split('>')[1].split('<')[0] + ': ' + g.split('>')[1].split('<')[0] + '-' + h.split('>')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        add = add.replace('&#x27;',"'")
        yield [website, loc.split('|')[0], name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
