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
    states = []
    urls = ['https://www.budget.com/en/locations/us','https://www.budget.com/en/locations/ca']
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<a href="/en/locations/us/' in line or '<a href="/en/locations/ca/' in line:
                lurl = 'https://www.budget.com' + line.split('href="')[1].split('"')[0]
                states.append(lurl)
    for state in states:
        print(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        RFound = False
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<h1>' in line2:
                RFound = True
            if RFound and '<a href="/en/locations/' in line2:
                lurl = 'https://www.budget.com' + line2.split('href="')[1].split('"')[0]
                if lurl.count('/') == 8:
                    locs.append(lurl)
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 'budget.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        store = loc.rsplit('/',1)[1]
        city = ''
        add = ''
        state = ''
        zc = ''
        country = ''
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"addressCountry": "' in line2:
                country = line2.split('"addressCountry": "')[1].split('"')[0]
                if 'C' in country:
                    country = 'CA'
                else:
                    country = 'US'
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0]
            if '"description":"' in line2:
                name = line2.split('"description":"')[1].split('"')[0] + ' (' + line2.split('"locationCode":"')[1].split('"')[0] + ')'
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
