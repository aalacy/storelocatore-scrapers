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
    url = 'https://www.betonel.com/diy/trouver-un-magasin/province'
    alllocs = []
    states = []
    cities = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<li><a href="/diy/trouver-un-magasin/' in line:
            states.append('https://www.dulux.ca/diy/store-locator' + line.split('/trouver-un-magasin')[1].split('"')[0])
    for state in states:
        print(('Pulling Province %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<li><a href="/diy/where-to-buy/ca/' in line2:
                cities.append('https://www.dulux.ca/diy/where-to-buy/ca/' + line2.split('/ca/')[1].split('"')[0])
    for city in cities:
        locs = []
        print(('Pulling City %s...' % city))
        r2 = session.get(city, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'p>More Info</p>' in line2:
                lurl = 'https://www.dulux.ca' + line2.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    locs.append(lurl)
        for loc in locs:
            print(('Pulling Location %s...' % loc))
            r2 = session.get(loc, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            lines = r2.iter_lines(decode_unicode=True)
            country = 'CA'
            typ = 'Store'
            website = 'dulux.ca'
            phone = ''
            name = ''
            add = ''
            city = ''
            state = ''
            zc = ''
            lat = '<MISSING>'
            lng = '<MISSING>'
            hours = ''
            store = ''
            for line2 in lines:
                if '<form method="post" action="' in line2:
                    store = line2.split('<form method="post" action="')[1].split('.aspx')[0].rsplit('-',1)[1]
                if '<h1>' in line2:
                    g = next(lines)
                    if '>' not in g:
                        g = next(lines)
                    name = g.split('>')[1].split('<')[0].strip().replace('\t','')
                    if ' in ' in name:
                        typ = name.split(' in ')[0]
                if '<span itemprop="streetAddress" id="street">' in line2:
                    Found = True
                    while Found:
                        g = next(lines)
                        if '<p>' in g:
                            Found = False
                    add = g.split('>')[1].split('<')[0]
                    g = next(lines)
                    if '>' in g:
                        add = add + ' ' + g.split('>')[1].split('<')[0]
                        add = add.strip()
                if 'addressLocality" id="city">' in line2:
                    city = line2.split('addressLocality" id="city">')[1].split('<')[0].strip().replace(',','')
                if 'addressRegion" id="state">' in line2:
                    state = line2.split('addressRegion" id="state">')[1].split('<')[0].strip()
                if 'postalCode" id="postal">' in line2:
                    zc = line2.split('postalCode" id="postal">')[1].split('<')[0].strip()
                if '<a href="tel:' in line2:
                    phone = line2.split('<a href="tel:')[1].split('"')[0]
                if '<img border="0" src="https://maps.googleapis.com' in line2:
                    lat = line2.split('<img border="0" src="https://maps.googleapis.com')[1].split('center=')[1].split(',')[0].strip()
                    lng = line2.split('<img border="0" src="https://maps.googleapis.com')[1].split('center=')[1].split(',')[1].split('&')[0].strip()
                if '<span class="day-of-week">' in line2:
                    day = line2.split('<span class="day-of-week">')[1].split('<')[0]
                if '<span class="opens">' in line2:
                    hrs = day + ': ' + next(lines).split('&')[0].strip().replace('\t','')
                if '<span class="closes">' in line2:
                    hrs = hrs + '-' + next(lines).split('<')[0].strip().replace('\t','')
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
            if phone == '':
                phone = '<MISSING>'
            if hours == '':
                hours = '<MISSING>'
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
