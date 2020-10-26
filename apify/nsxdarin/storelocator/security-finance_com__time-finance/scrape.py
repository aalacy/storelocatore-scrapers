import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import sgzip

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    for code in sgzip.for_radius(50):
        print(('Pulling Zip Code %s...' % code))
        url = 'https://www.securityfinance.com/wp-admin/admin-ajax.php?action=tba_locator_search&zip=' + code + '&radius=100&results=100'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if 'More info' in line:
                items = line.split('\\" href=\\"https:\\/\\/www.securityfinance.com\\/locations\\/')
                for item in items:
                    if '{"list":"' not in item:
                        lurl = 'https://www.securityfinance.com/locations/' + item.split('\\')[0]
                        if lurl not in locs:
                            locs.append(lurl)
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        print(('Pulling Location %s...' % loc))
        website = 'www.security-finance.com'
        typ = ''
        store = ''
        add = ''
        zc = ''
        state = ''
        city = ''
        country = ''
        name = ''
        phone = ''
        hours = ''
        NFound = False
        lat = '<MISSING>'
        lng = '<MISSING>'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<h1 class="location-name">' in line2:
                typ = line2.split('<h1 class="location-name">')[1].split('<')[0]
            if '"name": "' in line2 and NFound is False:
                NFound = True
                name = line2.split('"name": "')[1].split('"')[0]
            if '"addressCountry": "' in line2:
                country = line2.split('"addressCountry": "')[1].split('"')[0]
                if country == 'USA':
                    country = 'US'
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"branchCode": "' in line2:
                store = line2.split('"branchCode": "')[1].split('"')[0]
            if '><tr><td>' in line2:
                days = line2.split('><tr><td>')
                for day in days:
                    if '</td></tr' in day:
                        dayname = day.split('<')[0]
                        hrs = day.split('</td><td>')[1].split('</td>')[0].replace('<time>','').replace('</time>','')
                        if hours == '':
                            hours = dayname + ': ' + hrs
                        else:
                            hours = hours + '; ' + dayname + ': ' + hrs
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
