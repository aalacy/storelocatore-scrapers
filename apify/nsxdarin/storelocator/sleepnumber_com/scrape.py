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
    url = 'https://stores.sleepnumber.com/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'class="Directory-listLink" href="' in line:
            items = line.split('class="Directory-listLink" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(')')[0]
                    lurl = 'https://stores.sleepnumber.com/' + item.split('"')[0]
                    if count == '1':
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if 'class="Directory-listLink" href="' in line2:
                items = line2.split('class="Directory-listLink" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(')')[0]
                        lurl = 'https://stores.sleepnumber.com/' + item.split('"')[0]
                        if count == '1':
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if 'track="visitpage" href="../' in line2:
                items = line2.split('track="visitpage" href="../')
                for item in items:
                    if 'View Store Details' in item:
                        lurl = 'https://stores.sleepnumber.com/' + item.split('"')[0]
                        locs.append(lurl)
        for loc in locs:
            print('Pulling Location %s...' % loc)
            website = 'sleepnumber.com'
            typ = '<MISSING>'
            hours = ''
            name = ''
            add = ''
            city = ''
            state = ''
            country = 'US'
            zc = ''
            phone = ''
            store = ''
            lat = ''
            lng = ''
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '"name" id="location-name">' in line2:
                    name = line2.split('"name" id="location-name">')[1].split('<')[0]
                if '"dimension4":"' in line2:
                    add = line2.split('"dimension4":"')[1].split('"')[0]
                    zc = line2.split('"dimension5":"')[1].split('"')[0]
                    state = line2.split('"dimension2":"')[1].split('"')[0]
                    city = line2.split('"dimension3":"')[1].split('"')[0]
                if phone == '' and 'id="phone-main">' in line2:
                    phone = line2.split('id="phone-main">')[1].split('<')[0]
                if '<meta itemprop="latitude" content="' in line2:
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                if '<meta itemprop="longitude" content="' in line2:
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                if hours == '' and "days='[{" in line2:
                    days = line2.split("days='[{")[1].split("}]'>")[0].split('"day":"')
                    for day in days:
                        if 'intervals' in day:
                            if '"intervals":[{' not in day:
                                hrs = day.split('"')[0] + ': Closed'
                            else:
                                hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
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
