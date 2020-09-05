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
    url = 'https://www.hibbett.com/storedirectory'
    states = []
    ids = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<a href="/storedirectory?state=' in line:
            states.append('https://www.hibbett.com' + line.split('href="')[1].split('"')[0])
    for state in states:
        cities = []
        print(('Pulling State %s...' % state))
        r2 = session.get(state.replace('&amp;','&'), headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '/storedirectory?city=' in line2:
                cities.append('https://www.hibbett.com' + line2.split('href="')[1].split('"')[0])
        for city in cities:
            print(('Pulling City %s...' % city))
            locs = []
            r3 = session.get(city.replace('&amp;','&'), headers=headers)
            if r3.encoding is None: r3.encoding = 'utf-8'
            for line3 in r3.iter_lines(decode_unicode=True):
                if 'More Details</a>' in line3:
                    locs.append('https://www.hibbett.com/' + line3.split('href="')[1].split('"')[0])
            for loc in locs:
                name = ''
                add = ''
                city = ''
                state = ''
                store = loc.rsplit('/',1)[1]
                lat = ''
                lng = ''
                hours = ''
                country = 'US'
                zc = ''
                phone = ''
                print(('Pulling Location %s...' % loc))
                website = 'hibbett.com'
                typ = 'Store'
                r4 = session.get(loc, headers=headers)
                lines = r4.iter_lines(decode_unicode=True)
                for line4 in lines:
                    if '<title>' in line4 and name == '':
                        name = line4.split('<title>')[1].split(' |')[0]
                    if '<div itemprop="streetAddress">' in line4:
                        g = next(lines)
                        add = g.replace('\r','').replace('\t','').replace('\n','').strip()
                    if 'itemprop="addressLocality">' in line4:
                        city = line4.split('itemprop="addressLocality">')[1].split('<')[0].strip()
                        state = line4.split('itemprop="addressRegion">')[1].split('<')[0].strip()
                        zc = line4.split('itemprop="postalCode">')[1].split('<')[0].strip()
                    if '<a href="tel:' in line4:
                        phone = line4.split('<a href="tel:')[1].split('"')[0]
                    if '<form id="store-search-form">' in line4:
                        g = next(lines)
                        lat = g.split('value="')[1].split(',')[0].strip()
                        lng = g.split('value="')[1].split(',')[1].split('"')[0].strip()
                    if '<span class="label"><span>' in line4:
                        hrs = line4.split('span class="label"><span>')[1].split('<')[0]
                        g = next(lines)
                        hrs = hrs + ': ' + g.replace('\r','').replace('\t','').replace('\n','').strip()
                        hrs = hrs.replace('</span>','').replace('<span>','')
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                if phone == '':
                    phone = '<MISSING>'
                if hours == '':
                    hours = '<MISSING>'
                if store not in ids:
                    ids.append(store)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
