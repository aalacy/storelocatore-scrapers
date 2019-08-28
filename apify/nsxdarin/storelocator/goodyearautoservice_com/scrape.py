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
    states = []
    cities = []
    url = 'https://www.goodyear.com/en-US/tires/tire-shop?expand=states'
    r = session.get(url, headers=headers)
    alllocs = []
    lines = r.iter_lines()
    for line in lines:
        if 'data-tracking-cta-id="bbs-' in line:
            states.append('https://www.goodyear.com/' + line.split('href="')[1].split('"')[0])

    for state in states:
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '<li><a href="/en-US/tire-stores/' in line2:
                cities.append('https://www.goodyear.com/' + line2.split('href="')[1].split('"')[0])

    for city in cities:
        locs = []
        citystate = city.split('/tire-stores/')[1].split('/')[0]
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if '<a href="/en-US/tire-shop/' in line2:
                lurl = 'https://www.goodyear.com/' + line2.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    locs.append(lurl)

        for loc in locs:
            PageFound = False
            while PageFound is False:
                try:
                    PageFound = True
                    r3 = session.get(loc, headers=headers)
                    typ = 'Store'
                    website = 'www.goodyearautoservice.com'
                    country = 'US'
                    lines3 = r3.iter_lines()
                    name = ''
                    store = ''
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                    add = '<MISSING>'
                    city = '<MISSING>'
                    state = '<MISSING>'
                    zc = '<MISSING>'
                    hours = '<MISSING>'
                    phone = '<MISSING>'
                    for line3 in lines3:
                        if '<h1 class="page-title" itemprop="name">' in line3:
                            name = next(lines3).split('<')[0].strip().replace('\t','').replace('"',"'")
                        if '"name":"' in line3:
                            store = line3.split('"name":"')[1].split('"')[0]
                            lat = line3.split('"latitude":')[1].split(',')[0]
                            lng = line3.split('"longitude":')[1].split(',')[0]
                        if 'itemprop="streetAddress">' in line3:
                            add = line3.split('itemprop="streetAddress">')[1].split('<')[0].replace('"',"'")
                        if 'itemprop="addressLocality">' in line3:
                            city = line3.split('itemprop="addressLocality">')[1].split(',')[0]
                            try:
                                state = line3.split('&nbsp;')[1].split('<')[0]
                            except:
                                state = citystate
                        if 'itemprop="postalCode">' in line3:
                            zc = line3.split('itemprop="postalCode">')[1].split('<')[0]
                        if 'itemprop="telephone">' in line3:
                            phone = line3.split('itemprop="telephone">')[1].split('<')[0]
                        if 'Monday</span>' in line3:
                            hours = 'Mon: ' + next(lines3).split('>')[1].split('<')[0]
                        if 'itemprop="dayOfWeek">' in line3 and 'Monday' not in line3:
                            g = next(lines3)
                            hours = hours + '; ' + line3.split('"dayOfWeek">')[1].split('<')[0] + ': ' + g.split('>')[1].split('<')[0]
                    if add == '':
                        add = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                except:
                    PageFound = False

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
