import csv
import urllib2
from sgrequests import SgRequests
import time

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
    url = 'https://www.shiekh.com/store-list'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="brand-item-link" href="https://www.shiekh.com/stores/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if 'online-store' not in line:
                locs.append(lurl)
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        lat = ''
        lng = ''
        hours = ''
        zc = '<MISSING>'
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'shiekhshoes.com'
        typ = 'Store'
        store = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<title>' in line2:
                name = line2.split('>')[1].split('<')[0].strip()
            if '<p itemprop="streetAddress"' in line2:
                add = line2.split('>')[1].split('<')[0].strip()
            if '"address":"' in line2:
                phone = line2.split('"phone":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                store = line2.split('"storelocator_id":"')[1].split('"')[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="openingHours" content="' in line2:
                hrs = line2.split('itemprop="openingHours" content="')[1].split('"')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        country = 'US'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if '404 Not Found' not in name:
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        time.sleep(3)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
