import csv
import urllib2
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
    canada = ['ab','mb','bc','sk','on','nl','ns','nb','qc','pq']
    url = 'https://www.hickoryfarms.com/locations-results?dwfrm_storelocator_countryCode=US&dwfrm_storelocator_distanceUnit=mi&dwfrm_storelocator_postalCode=10002&dwfrm_storelocator_maxdistance=50000.0&dwfrm_storelocator_findbyzip=Search'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="store-details-link"' in line:
            lurl = line.split('href="')[1].split('"')[0]
            st = line.split('/us/')[1].split('/')[0]
            if st in canada:
                locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'hickoryfarms.ca'
        typ = '<MISSING>'
        country = 'CA'
        hours = ''
        phone = ''
        add = ''
        name = ''
        city = ''
        state = ''
        zc = ''
        lat = ''
        lng = ''
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('<')[0]
            if '<div itemprop="streetAddress">' in line2:
                add = line2.split('<div itemprop="streetAddress">')[1].split('<')[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split('<')[0].strip()
            if '<div itemprop="telephone">' in line2:
                phone = line2.split('<div itemprop="telephone">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
            if '<meta itemprop="longitude" content="' in line2:
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
        hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        phone = phone.replace('&#40;','(').replace('&#41;',')')
        if lat == '':
            lat = '<MISSING>'
        if lng == '':
            lng = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
