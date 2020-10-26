import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.umamiburger.com/locations/'
    locs = []
    cities = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '<div class="location-regions__item">' in line:
            lurl = next(lines).split('href="')[1].split('"')[0]
            if '/locations/' in lurl and 'locations/other' not in lurl:
                cities.append(lurl)
    for city in cities:
        r2 = session.get(city, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines2 = r2.iter_lines(decode_unicode=True)
        print(('Pulling Region %s...' % city))
        for line2 in lines2:
            if '<div class="col-xs-12 col-x-sm-6 col-sm-6 col-md-4">' in line2:
                locs.append(next(lines2).split('href="')[1].split('"')[0])
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        website = 'www.umamiburger.com'
        typ = 'Restaurant'
        store = '<MISSING>'
        add = ''
        zc = ''
        state = ''
        city = ''
        country = 'US'
        name = ''
        phone = ''
        hours = ''
        lat = ''
        lng = ''
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if "lat : " in line2:
                lat = line2.split("lat : ")[1].split(',')[0]
            if "long: " in line2:
                lng = line2.split("long: ")[1].split(',')[0]
            if '"openingHours": ["' in line2:
                hours = line2.split('"openingHours": ["')[1].split('"]')[0].replace('","','; ')
        if phone == '':
            phone = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
