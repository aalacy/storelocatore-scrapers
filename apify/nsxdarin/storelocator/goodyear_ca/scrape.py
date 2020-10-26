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
    states = []
    url = 'https://www.goodyear.ca/en-CA/services/find-a-tire-store'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    locs = []
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '<li><a rel="t-sd-3' in line:
            surl = 'https://www.goodyear.ca' + line.split('href="')[1].split('"')[0]
            states.append(surl)

    for state in states:
        print(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'details#overview"' in line2:
                rurl = 'https://www.goodyear.ca' + line2.split('href="')[1].split('"')[0]
                if rurl not in locs:
                    locs.append(rurl)

    for loc in locs:
        print(('Pulling Location %s...' % loc))
        r3 = session.get(loc, headers=headers)
        if r3.encoding is None: r3.encoding = 'utf-8'
        typ = 'Retailer'
        website = 'www.goodyear.ca'
        country = 'CA'
        hours = ''
        store = '<MISSING>'
        lines3 = r3.iter_lines(decode_unicode=True)
        for line3 in lines3:
            if '<h1 itemprop="name"><b>' in line3:
                name = line3.split('<h1 itemprop="name"><b>')[1].split('<')[0]
            if '<span itemprop="addressRegion">' in line3:
                state = line3.split('<span itemprop="addressRegion">')[1].split('<')[0]
            if '<span itemprop="postalCode">' in line3:
                zc = line3.split('<span itemprop="postalCode">')[1].split('<')[0]
            if '<span itemprop="addressLocality">' in line3:
                city = line3.split('<span itemprop="addressLocality">')[1].split('<')[0]
            if '<span itemprop="streetAddress">' in line3:
                add = line3.split('<span itemprop="streetAddress">')[1].split('<')[0]
            if '<span itemprop="telephone">' in line3 and '</span>' in line3:
                phone = line3.split('<span itemprop="telephone">')[1].split('<')[0]
            if '<span itemprop="dayOfWeek">' in line3:
                if hours == '':
                    hours = line3.split('<span itemprop="dayOfWeek">')[1].split('<')[0] + ': '
                else:
                    hours = hours + '; ' + line3.split('<span itemprop="dayOfWeek">')[1].split('<')[0] + ': '
            if '<span itemprop="opens">' in line3:
                hours = hours + line3.split('<span itemprop="opens">')[1].split('<')[0]
            if 'class="end-latitude"' in line3:
                lat = line3.split('<input type="hidden" value="')[1].split('"')[0]
                lng = line3.split('<input type="hidden" value="')[2].split('"')[0]
        if phone == '':
            phone = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
