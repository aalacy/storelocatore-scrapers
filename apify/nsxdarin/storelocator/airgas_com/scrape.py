import csv
import urllib2
import requests
import sgzip
import time

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    stores = []
    for code in sgzip.for_radius(100):
        print('Pulling Zip %s...' % code)
        url = 'https://www.airgas.com/store-finder'
        payload = {'query': code,
               'radius': '100',
               'type': 'BRANCH',
               '_requestConfirmationToken': '231814d4c8742da3c6e0b717dbe424a3d9f55914'
               }
        r = session.post(url, headers=headers, data=payload)
        lines = r.iter_lines()
        for line in lines:
            if '<div class="map-information">' in line:
                next(lines)
                g = next(lines)
                name = g.split('<')[0].strip().replace('\t','')
                next(lines)
                next(lines)
                g = next(lines)
                try:
                    add = g.split('>')[1].split('<')[0]
                except:
                    add = ''
                next(lines)
                g = next(lines)
                store = '<MISSING>'
                typ = 'BRANCH'
                website = 'airgas.com'
                phone = ''
                lat = ''
                lng = ''
                try:
                    city = g.split('>')[1].split(',')[0]
                    state = g.split('&nbsp;')[1]
                    zc = g.split('&nbsp;')[3].split('<')[0]
                    country = 'US'
                except:
                    city = ''
                    state = ''
                    zc = ''
                    country = ''
            if '<p class="findabranch_callout">' in line:
                next(lines)
                g = next(lines)
                phone = g.strip().replace('\r','').replace('\n','').replace('\t','')
            if 'href="https://www.google.com/maps/dir/' in line:
                lat = line.split('href="https://www.google.com/maps/dir/')[1].split(',')[0]
                lng = line.split('href="https://www.google.com/maps/dir/')[1].split(',')[1].split('/')[0]
                hours = '<MISSING>'
                info = add + ':' + city + ':' + state + ':' + zc
                if info not in stores and country == 'US':
                    if add != '':
                        if zc == '':
                            zc = '<MISSING>'
                        if lat == '':
                            lat = '<MISSING>'
                        if lng == '':
                            lng = '<MISSING>'
                        if phone == '':
                            phone = '<MISSING>'
                        if city == '':
                            city = '<MISSING>'
                        stores.append(info)
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
