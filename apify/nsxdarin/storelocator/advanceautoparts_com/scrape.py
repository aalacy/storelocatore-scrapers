import csv
from sgrequests import SgRequests
import time

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
    urls = ['https://stores.advanceautoparts.com/']
    states = []
    cities = []
    locs = []
    allstores = []
    website = 'advanceautoparts.com'
    typ = '<MISSING>'
    country = '<MISSING>'
    canada = ['PE','NB','MB','BC','ON','QC','AB','NS','NL']
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '<a class="Directory-listLink" href="' in line:
                items = line.split('<a class="Directory-listLink" href="')
                for item in items:
                    if ' data-count="(' in item:
                        count = item.split(' data-count="(')[1].split(')')[0]
                        if count != '1':
                            states.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
                        else:
                            locs.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
    for state in states:
        #print('Pulling State %s...' % state)
        r = session.get(state, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '<a class="Directory-listLink" href="' in line:
                items = line.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-ya-track="todirectory" data-count="(' in item:
                        count = item.split('data-ya-track="todirectory" data-count="(')[1].split(')')[0]
                        if count != '1':
                            cities.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
                        else:
                            locs.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
                                
    for city in cities:
        #print('Pulling City %s...' % city)
        r = session.get(city, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '<a class="Teaser-titleLink" href="..' in line:
                items = line.split('<a class="Teaser-titleLink" href="..')
                for item in items:
                    if 'data-ya-track="businessname">' in item:
                        locs.append('https://stores.advanceautoparts.com/' + item.split('"')[0].replace('..',''))
    for loc in locs:
        loc = loc.replace('&#39;','%27').replace('.com//','.com/')
        #print('Pulling Location %s...' % loc)
        LFound = True
        tries = 0
        while LFound:
            try:
                LFound = False
                tries = tries + 1
                typ = 'Advance Auto Parts'
                r = session.get(loc, headers=headers, timeout=5)
                name = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                lat = ''
                lng = ''
                hours = ''
                country = ''
                phone = ''
                store = ''
                LocFound = False
                NFound = False
                for line in r.iter_lines():
                    line = str(line.decode('utf-8'))
                    if NFound is False and '"Nap-heading Heading Heading--h1">' in line:
                        NFound = True
                        name = line.split('"Nap-heading Heading Heading--h1">')[1].split('<')[0].strip().replace('<span>','').replace('  ',' ')
                    if '"store_id":"' in line:
                        store = line.split('"store_id":"')[1].split('"')[0]
                    if '"line1":"' in line and add == '':
                        add = line.split('"line1":"')[1].split('"')[0]
                        city = line.split(':{"city":"')[1].split('"')[0]
                        state = line.split(',"region":"')[1].split('"')[0]
                        zc = line.split('"postalCode":"')[1].split('"')[0]
                        country = line.split('"countryCode":"')[1].split('"')[0]
                        if '"line2":null' not in line:
                            add = add + ' ' + line.split('"line2":"')[1].split('"')[0]
                    if ',"mainPhone":{"' in line:
                        phone = line.split(',"mainPhone":{"')[1].split('"display":"')[1].split('"')[0]
                    if '<meta itemprop="latitude" content="' in line:
                        lat = line.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                        lng = line.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                    if '"normalHours":[' in line:
                        days = line.split('"normalHours":[')[1].split(']},"')[0].split('"day":"')
                        for day in days:
                            if '"isClosed":' in day:
                                if '"isClosed":true' in day:
                                    hrs = day.split('"')[0] + ': Closed'
                                else:
                                    hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                if store not in allstores:
                    allstores.append(store)
                    if state == '':
                        state = 'PR'
                    if state == 'PR':
                        country = 'US'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                if tries <= 3:
                    LFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
