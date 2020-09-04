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
    states = []
    cities = []
    locs = []
    url = 'https://www.tuesdaymorning.com/stores/index.html'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if '<span class="Directory-listLinkCount">(' in item:
                    count = item.split('<span class="Directory-listLinkCount">(')[1].split(')')[0]
                    lurl = 'https://www.tuesdaymorning.com/stores/' + item.split('"')[0]
                    if count == '1':
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        print(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'class="Directory-listLink" href="' in line2:
                items = line2.split('class="Directory-listLink" href="')
                for item in items:
                    if 'Directory-listLinkCount">(' in item:
                        count = item.split('Directory-listLinkCount">(')[1].split(')')[0]
                        lurl = 'https://www.tuesdaymorning.com/stores/' + item.split('"')[0]
                        if count == '1':
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        #print('Pulling City %s...' % city)
        r3 = session.get(city, headers=headers)
        if r3.encoding is None: r3.encoding = 'utf-8'
        for line3 in r3.iter_lines(decode_unicode=True):
            if '<a class="Teaser-titleLink" href="..' in line3:
                items = line3.split('<a class="Teaser-titleLink" href="..')
                for item in items:
                    if '<span class="LocationName">' in item:
                        locs.append('https://www.tuesdaymorning.com/stores' + item.split('"')[0])
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 'tuesdaymorning.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        city = ''
        add = ''
        state = ''
        country = 'US'
        phone = ''
        zc = ''
        lat = ''
        lng = ''
        phone = ''
        hours = ''
        Found = False
        Closed = False
        r3 = session.get(loc, headers=headers)
        if r3.encoding is None: r3.encoding = 'utf-8'
        for line3 in r3.iter_lines(decode_unicode=True):
            if '<meta name="description" content="' in line3:
                desc = line3.split('<meta name="description" content="')[1].split('"')[0]
                if 'CLOSED' in desc:
                    Closed = True
                name = line3.split('content="Visit your local ')[1].split(' at')[0]
            if Found is False and 'class="LocationName-geo">' in line3:
                Found = True
                phone = line3.split('<a class="Phone-link" href="tel:+')[1].split('"')[0]
            if '"dimension4":"' in line3:
                add = line3.split('"dimension4":"')[1].split('"')[0]
                city = line3.split('"dimension3":"')[1].split('"')[0]
                state = line3.split('"dimension2":"')[1].split('"')[0]
                zc = line3.split('"dimension5":"')[1].split('"')[0]
            if '<meta itemprop="latitude" content="' in line3:
                lat = line3.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line3.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if '"c_lid":"' in line3:
                store = line3.split('"c_lid":"')[1].split('"')[0]
            if 'Store Details</h2>' in line3:
                days = line3.split('Store Details</h2>')[1].split("days='[{")[1].split("}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals"' in day:
                        if '"isClosed":true' in day:
                            hrs = day.split('"')[0] + ': Closed'
                        elif 'dailyHolidayHours' not in day:
                            hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        else:
                            hrs = None
                        if hours == '' and hrs:
                            hours = hrs
                        elif hrs:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
