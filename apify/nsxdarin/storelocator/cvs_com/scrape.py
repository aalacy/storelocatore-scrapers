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
    locs = []
    donelocs = []
    states = []
    url = 'https://www.cvs.com/store-locator/cvs-pharmacy-locations'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<a href="/store-locator/cvs-pharmacy-locations/' in line:
            states.append('https://www.cvs.com' + line.split('href="')[1].split('"')[0])
    for state in states:
        cities = []
        print(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<a href="/store-locator/cvs-pharmacy-locations/' in line2:
                cities.append('https://www.cvs.com' + line2.split('href="')[1].split('"')[0])
        for city in cities:
            r2 = session.get(city, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            print(('Pulling City %s...' % city))
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<a href="/store-locator/cvs-pharmacy-address/' in line2:
                    lurl = 'https://www.cvs.com' + line2.split('href="')[1].split('"')[0]
                    if lurl not in locs:
                        locs.append(lurl)
            for loc in locs:
                if loc not in donelocs:
                    LFound = True
                    lcount = 0
                    while LFound:
                        try:
                            lcount = lcount + 1
                            print(('Pulling Location %s-%s...' % (loc, str(lcount))))
                            website = 'cvs.com'
                            typ = '<MISSING>'
                            hours = ''
                            name = 'CVS Pharmacy'
                            add = ''
                            city = ''
                            state = ''
                            zc = ''
                            country = 'US'
                            store = ''
                            phone = ''
                            lat = ''
                            lng = ''
                            Found = False
                            r3 = session.get(loc, headers=headers)
                            if r3.encoding is None: r3.encoding = 'utf-8'
                            for line3 in r3.iter_lines(decode_unicode=True):
                                if add == '' and '"streetAddress": "' in line3:
                                    LFound = False
                                    add = line3.split('"streetAddress": "')[1].split('"')[0]
                                if city == '' and '"addressLocality": "' in line3:
                                    city = line3.split('"addressLocality": "')[1].split('"')[0]
                                if state == '' and '"addressRegion": "' in line3:
                                    state = line3.split('"addressRegion": "')[1].split('"')[0]
                                if zc == '' and '"postalCode": "' in line3:
                                    zc = line3.split('"postalCode": "')[1].split('"')[0]
                                if phone == '' and '"telephone": "' in line3:
                                    phone = line3.split('"telephone": "')[1].split('"')[0]
                                if '"latitude": "' in line3:
                                    lat = line3.split('"latitude": "')[1].split('"')[0]
                                if '"longitude": "' in line3:
                                    lng = line3.split('"longitude": "')[1].split('"')[0]
                                if 'store_id : "' in line3 and 'cvs' not in line3:
                                    store = line3.split('store_id : "')[1].split('"')[0]
                                if '"openingHours":' in line3 and hours == '':
                                    Found = True
                                if Found and ']' in line3:
                                    Found = False
                                if Found and '"' in line3 and 'openingHours' not in line3:
                                    hrs = line3.split('"')[1]
                                    if hours == '':
                                        hours = hrs
                                    else:
                                        hours = hours + '; ' + hrs
                            if hours == '':
                                hours = '<MISSING>'
                            if phone == '':
                                phone = '<MISSING>'
                            hours = hours.replace(':00:00',':00').replace(':30:00',':30')
                            if loc not in donelocs and add != '':
                                donelocs.append(loc)
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                        except:
                            if lcount <= 3:
                                LFound = True
                            else:
                                LFound = False

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
