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
    urls = ['https://stores.nordstromrack.com/ca','https://stores.nordstromrack.com/us']
    for url in urls:
        locs = []
        states = []
        cities = []
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"Directory-listLink" href="' in line:
                items = line.split('"Directory-listLink" href="')
                for item in items:
                    if '<span class="Directory-listLinkText">' in item:
                        lurl = 'https://stores.nordstromrack.com/' + item.split('"')[0]
                        count = item.split('data-count="(')[1].split(')')[0]
                        if count != '1':
                            if 'honolulu' not in lurl and 'washington' not in lurl:
                                states.append(lurl)
                            else:
                                cities.append(lurl)
                        else:
                            locs.append(lurl)
        for state in states:
            print(('Pulling State %s...' % state))
            r2 = session.get(state, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<a class="Directory-listLink" href="../' in line2:
                    items = line2.split('<a class="Directory-listLink" href="../')
                    for item in items:
                        if '<span class="Directory-listLinkText">' in item:
                            lurl = 'https://stores.nordstromrack.com/' + item.split('"')[0]
                            count = item.split('data-count="(')[1].split(')')[0]
                            if count != '1':
                                cities.append(lurl)
                            else:
                                locs.append(lurl)
        for city in cities:
            print(('Pulling City %s...' % city))
            r2 = session.get(city, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<a class="Teaser-titleLink" href="../../' in line2:
                    items = line2.split('<a class="Teaser-titleLink" href="../../')
                    for item in items:
                        if 'data-ya-track="businessname">' in item:
                            lurl = 'https://stores.nordstromrack.com/' + item.split('"')[0]
                            locs.append(lurl)
        for loc in locs:
            print(('Pulling Location %s...' % loc))
            website = 'nordstromrack.com'
            typ = 'Store'
            store = '<MISSING>'
            hours = ''
            r2 = session.get(loc, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if 'id="telephone">' in line2:
                    phone = line2.split('id="telephone">')[1].split('<')[0]
                if 'itemprop="openingHours" content="' in line2:
                    items = line2.split('itemprop="openingHours" content="')
                    for item in items:
                        if '<td class="c-location-hours-details-row-day">' in item:
                            if hours == '':
                                hours = item.split('"')[0]
                            else:
                                hours = hours + '; ' + item.split('"')[0]
                if '<span class="c-bread-crumbs-name">' in line2:
                    name = line2.split('<span class="c-bread-crumbs-name">')[1].split('<')[0]
                if '<meta itemprop="latitude" content="' in line2:
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                if 'country_code: "' in line2:
                    country = line2.split('country_code: "')[1].split('"')[0]
                    state = line2.split('state_code: "')[1].split('"')[0]
                    city = line2.split('city: "')[1].split('"')[0]
                    add = line2.split('address: "')[1].split('"')[0]
                    zc = line2.split('zip_code: "')[1].split('"')[0]
                    country = line2.split('country_code: "')[1].split('"')[0]
                    country = line2.split('country_code: "')[1].split('"')[0]
                    country = line2.split('country_code: "')[1].split('"')[0]
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
