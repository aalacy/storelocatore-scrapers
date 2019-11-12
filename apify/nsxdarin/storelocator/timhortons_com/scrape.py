import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    urls = ['https://locations.timhortons.com/us.html','https://locations.timhortons.com/ca.html']
    for url in urls:
        locs = []
        states = []
        cities = []
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '"c-directory-list-content-item-link" href="' in line:
                items = line.split('"c-directory-list-content-item-link" href="')
                for item in items:
                    if '</a></li>' in item:
                        lurl = 'https://locations.timhortons.com/' + item.split('"')[0]
                        if lurl.count('/') == 6:
                            if lurl not in locs:
                                locs.append(lurl)
                        if lurl.count('/') == 5:
                            cities.append(lurl)
                        if lurl.count('/') == 4:
                            states.append(lurl)
        for state in states:
            print('Pulling State %s...' % state)
            r2 = session.get(state, headers=headers)
            for line2 in r2.iter_lines():
                if '<a class="c-directory-list-content-item-link" href="../' in line2:
                    items = line2.split('<a class="c-directory-list-content-item-link" href="../')
                    for item in items:
                        if '</a></li>' in item:
                            lurl = 'https://locations.timhortons.com/' + item.split('"')[0]
                            if lurl.count('/') == 6:
                                if lurl not in locs:
                                    locs.append(lurl)
                            else:
                                cities.append(lurl)
        for city in cities:
            print('Pulling City %s...' % city)
            r2 = session.get(city, headers=headers)
            for line2 in r2.iter_lines():
                if '"Teaser-titleLink"data-ya-track="dir_visit_page"href="../../' in line2:
                    items = line2.split('"Teaser-titleLink"data-ya-track="dir_visit_page"href="../../')
                    for item in items:
                        if '<span class="LocationName">' in item:
                            lurl = 'https://locations.timhortons.com/' + item.split('"')[0]
                            if lurl not in locs:
                                locs.append(lurl)
        for loc in locs:
            r2 = session.get(loc, headers=headers)
            website = 'timhortons.com'
            typ = 'Restaurant'
            name = ''
            add = ''
            city = ''
            state = ''
            zc = ''
            store = ''
            phone = ''
            lat = ''
            lng = ''
            hours = ''
            if 'ca.html' in url:
                country = 'CA'
            else:
                country = 'US'
            for line2 in r2.iter_lines():
                if '{"ids":' in line2:
                    store = line2.split('{"ids":')[1].split(',')[0]
                if '<span class="LocationName-geo">' in line2:
                    name = line2.split('<span class="LocationName-geo">')[1].split('<')[0]
                if '<meta itemprop="streetAddress" content="' in line2:
                    add = line2.split('<meta itemprop="streetAddress" content="')[1].split('"')[0]
                    city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                    state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                    zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                    phone = line2.split('id="telephone">')[1].split('<')[0]
                if '<meta itemprop="latitude" content="' in line2:
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                if "data-days='[{" in line2:
                    days = line2.split("data-days='[{")[1].split("]}]'")[0].split('"day":"')
                    for day in days:
                        if '"intervals"' in day:
                            if hours == '':
                                try:
                                    hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                except:
                                    hours = day.split('"')[0] + ': CLOSED'
                            else:
                                try:
                                    hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                except:
                                    hours = hours + '; ' + day.split('"')[0] + ': CLOSED'
            hours = hours.replace(' 0-0',' Open 24 Hours;')
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
