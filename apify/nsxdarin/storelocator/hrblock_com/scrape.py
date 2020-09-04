import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    url = 'https://www.hrblock.com/tax-offices/local/'
    alllocs = []
    states = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'href="/tax-offices/local/' in line:
            lurl = 'https://hrblock.com' + line.split('href="')[1].split('"')[0]
            states.append(lurl)
    for state in states:
        #print('Pulling State %s...' % state)
        cities = []
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '{"loc":"b","nm":"city' in line2:
                lurl = 'https://hrblock.com' + line2.split('href="')[1].split('"')[0]
                cities.append(lurl)
        for city in cities:
            locs = []
            #print('Pulling City %s...' % city)
            r3 = session.get(city, headers=headers)
            if r3.encoding is None: r3.encoding = 'utf-8'
            for line3 in r3.iter_lines(decode_unicode=True):
                if 'View Office Info' in line3:
                    lurl = 'https://hrblock.com' + line3.split('href="')[1].split('"')[0]
                    if lurl not in alllocs:
                        alllocs.append(lurl)
                        r4 = session.get(lurl, headers=headers)
                        lines = r4.iter_lines(decode_unicode=True)
                        website = 'hrblock.com'
                        typ = 'Location'
                        name = 'H&R Block'
                        store = lurl.rsplit('/',1)[1]
                        hours = '<MISSING>'
                        add = ''
                        city = ''
                        country = 'US'
                        state = ''
                        zc = ''
                        phone = ''
                        lat = ''
                        lng = ''
                        for line4 in lines:
                            if '<span itemprop="streetAddress">' in line4:
                                if add == '':
                                    add = line4.split('<span itemprop="streetAddress">')[1].split('<')[0]
                                else:
                                    add = add + ' ' + line4.split('<span itemprop="streetAddress">')[1].split('<')[0]
                            if '<span itemprop="addressLocality">' in line4:
                                city = line4.split('<span itemprop="addressLocality">')[1].split('<')[0]
                            if '<span itemprop="addressRegion">' in line4:
                                state = line4.split('<span itemprop="addressRegion">')[1].split('<')[0]
                            if '<span itemprop="postalCode">' in line4:
                                zc = line4.split('<span itemprop="postalCode">')[1].split('<')[0]
                            if '<a href="tel:' in line4:
                                phone = line4.split('<a href="tel:')[1].split('"')[0]
                            if 'itemprop="latitude"' in line4:
                                lat = line4.split('content="')[1].split('"')[0]
                            if 'itemprop="longitude"' in line4:
                                lng = line4.split('content="')[1].split('"')[0]
                        if lat == '':
                            lat = '<MISSING>'
                        if lng == '':
                            lng = '<MISSING>'
                        if add != '':
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
