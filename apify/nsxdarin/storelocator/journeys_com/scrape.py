import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('journeys_com')



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
    url = 'https://www.journeys.com/stores_all'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'class="link-store-info btn-action">' in line:
            locs.append('https://www.journeys.com' + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        AFound = False
        lines = r2.iter_lines(decode_unicode=True)
        website = 'journeys.com'
        add = ''
        hours = ''
        for line2 in lines:
            if '<p itemprop="streetAddress">' in line2:
                AFound = True
            if AFound and '<span itemprop="addressLocality">' in line2:
                website = 'journeys.com'
                AFound = False
                city = line2.split('span itemprop="addressLocality">')[1].split('<')[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('"postalCode">')[1].split('<')[0]
                country = 'US'
            if AFound and '<p item' not in line2 and '</p>' in line2 and '<p>' in line2:
                add = add + ' ' + line2.split('<p>')[1].split('<')[0]
            if '<h2 itemprop="name">' in line2:
                name = line2.split('<h2 itemprop="name">')[1].split('<')[0].strip()
                try:
                    store = name.split('#')[1]
                except:
                    store = '<MISSING>'
                typ = name.split('#')[0].title().strip()
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
        if add == '':
            add = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
