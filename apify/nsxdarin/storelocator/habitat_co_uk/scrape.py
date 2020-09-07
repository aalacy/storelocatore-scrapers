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
    url = 'https://www.habitat.co.uk/storelocator'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'Store information</a>' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        website = 'habitat.co.uk'
        typ = ''
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'GB'
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"url":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                typ = line2.split('"brand":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0].strip()
                state = '<MISSING>'
                zc = line2.split('"postalCode":"')[1].split('"')[0].strip()
                add = line2.split('"streetAddress":"')[1].split('"')[0].strip()
                hours = line2.split('"openingHours":[')[1].split(']')[0].replace('","','; ').replace('"','')
            if 'center: { lat:' in line2:
                lat = line2.split('center: { lat:')[1].split(',')[0].strip()
                lng = line2.split('lng:')[1].split('}')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        add = add.replace('\\u2019',"'")
        name = name.replace('\\u2019',"'")
        if 'Inside' in add:
            if ',' in add:
                add = add.split(',',1)[1].strip()
        if city == '':
            city = add.split(',')[1].strip()
            add = add.split(',')[1].strip()
        if ',' in city:
            add = city.split(',')[0].strip()
            city = city.split(',')[1].strip()
        if 'nine-elms' in loc:
            city = 'London'
            add = '62 Wandsworth Road'
        if 'wandsworth' in loc:
            city = 'London'
            add = '45 Garratt Lane'
        if 'heaton-newcastle' in loc:
            city = 'Newcastle'
            add = 'Etherstone Avenue'
        if 'London' in name:
            city = 'London'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
