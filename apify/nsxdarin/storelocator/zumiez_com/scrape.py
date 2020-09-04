import csv
from sgrequests import SgRequests
import json

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
    url = 'https://www.zumiez.com/storelocator/search/latlng/?lat=40.7135097&lng=-73.9859414&radius=10000'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for item in json.loads(r.content):
        store = item['locator_id']
        website = 'zumiez.com'
        typ = 'Store'
        loc = 'https://www.zumiez.com/storelocator/store/index/id/' + store
        hours = ''
        country = 'US'
        name = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<title>' in line2 and name == '':
                name = line2.split('<title>')[1].split(' |')[0]
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0].replace(',','')
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0]
            if 'itemprop="latitude">' in line2:
                lat = line2.split('content="')[1].split('"')[0]
            if 'itemprop="longitude">' in line2:
                lng = line2.split('content="')[1].split('"')[0]
            if 'itemprop="openingHours" datetime="' in line2:
                hrs = line2.split('itemprop="openingHours" datetime="')[1].split('"')[0].replace('&nbsp;',' ')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
