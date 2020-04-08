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
    states = []
    cities = []
    url = 'https://locations.dignityhealth.org/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if '</a><span class="Directory-listLinkCount' in item:
                    states.append('https://locations.dignityhealth.org/' + item.split('"')[0])
    for state in states:
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<a class="Directory-listLink" href="' in line2:
                items = line2.split('<a class="Directory-listLink" href="')
                for item in items:
                    if '</a><span class="Directory-listLinkCount">(' in item:
                        count = item.split('</a><span class="Directory-listLinkCount">(')[1].split(')')[0]
                        lurl = 'https://locations.dignityhealth.org/' + item.split('"')[0]
                        if count == '1':
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if '<a class="Teaser-titleLink" href="' in line2:
                items = line2.split('<a class="Teaser-titleLink" href="')
                for item in items:
                    if 'data-ya-track="businessname">' in item:
                        locs.append('https://locations.dignityhealth.org/' + item.split('"')[0])
    for loc in locs:
        loc = loc.replace('&#39;','%27').replace('&amp;','%26')
        print('Pulling Location %s...' % loc)
        website = 'dignityhealth.org'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = ''
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if 'id="location-name" itemprop="name">' in line2:
                name = line2.split('id="location-name" itemprop="name">')[1].split('<')[0]
            if '[{"altTagText":"' in line2 and add == '':
                add = line2.split('"address":')[1].split('"line1":"')[1].split('"')[0]
                city = line2.split('{"city":"')[1].split('"')[0]
                state = line2.split(',"region":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if ',"number":"' in line2:
                phone = line2.split(',"number":"')[1].split('"')[0].replace('+1','')
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if ',"id":"' in line2:
                store = line2.split(',"id":"')[1].split('"')[0]
            if '><span class="c-hours-today js-hours-today" data-days=' in line2 and hours == '':
                days = line2.split('><span class="c-hours-today js-hours-today" data-days=')[1].split("}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals"' in day:
                        dname = day.split('"')[0]
                        if '"isClosed":true' in day:
                            hrs = dname + ': Closed'
                        else:
                            if '{"end":2359,"start":0}' in day:
                                hrs = dname + ': 24 Hours'
                            else:
                                hrs = dname + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
