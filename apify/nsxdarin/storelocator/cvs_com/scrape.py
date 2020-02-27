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
    url = 'https://www.cvs.com/store-locator/cvs-pharmacy-locations'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a href="/store-locator/cvs-pharmacy-locations/' in line:
            states.append('https://www.cvs.com' + line.split('href="')[1].split('"')[0])
    for state in states:
        cities = []
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<a href="/store-locator/cvs-pharmacy-locations/' in line2:
                cities.append('https://www.cvs.com' + line2.split('href="')[1].split('"')[0])
        for city in cities:
            r2 = session.get(city, headers=headers)
            print('Pulling City %s...' % city)
            for line2 in r2.iter_lines():
                if '<a href="/store-locator/cvs-pharmacy-address/' in line2:
                    lurl = 'https://www.cvs.com' + line2.split('href="')[1].split('"')[0]
                    if lurl not in locs:
                        locs.append(lurl)
        for loc in locs:
            LFound = True
            while LFound:
                try:
                    print('Pulling Location %s...' % loc)
                    website = 'cvs.com'
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
                    Found = False
                    r2 = session.get(loc, headers=headers)
                    for line2 in r2.iter_lines():
                        if name == '' and '"name": "' in line2:
                            name = line2.split('"name": "')[1].split('"')[0]
                            LFound = False
                        if add == '' and '"streetAddress": "' in line2:
                            add = line2.split('"streetAddress": "')[1].split('"')[0]
                        if city == '' and '"addressLocality": "' in line2:
                            city = line2.split('"addressLocality": "')[1].split('"')[0]
                        if state == '' and '"addressRegion": "' in line2:
                            state = line2.split('"addressRegion": "')[1].split('"')[0]
                        if zc == '' and '"postalCode": "' in line2:
                            zc = line2.split('"postalCode": "')[1].split('"')[0]
                        if phone == '' and '"telephone": "' in line2:
                            phone = line2.split('"telephone": "')[1].split('"')[0]
                        if '"latitude": "' in line2:
                            lat = line2.split('"latitude": "')[1].split('"')[0]
                        if '"longitude": "' in line2:
                            lng = line2.split('"longitude": "')[1].split('"')[0]
                        if 'store_id : "' in line2 and 'cvs' not in line2:
                            store = line2.split('store_id : "')[1].split('"')[0]
                        if '"openingHours":' in line2 and hours == '':
                            Found = True
                        if Found and ']' in line2:
                            Found = False
                        if Found and '"' in line2 and 'openingHours' not in line2:
                            hrs = line2.split('"')[1]
                            if hours == '':
                                hours = hrs
                            else:
                                hours = hours + '; ' + hrs
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    hours = hours.replace(':00:00',':00').replace(':30:00',':30')
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                except:
                    LFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
