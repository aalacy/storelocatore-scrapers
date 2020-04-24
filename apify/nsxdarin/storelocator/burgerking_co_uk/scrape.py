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
    url = 'https://locations.burgerking.co.uk/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'rel="alternate" hreflang="en_GB" href="https://locations.burgerking.co.uk/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl.count('/') == 4:
                locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'burgerking.co.uk'
        typ = 'Restaurant'
        hours = ''
        country = 'GB'
        r2 = session.get(loc, headers=headers)
        name = ''
        add = ''
        city = ''
        state = '<MISSING>'
        zc = ''
        phone = ''
        store = ''
        lat = ''
        lng = ''
        for line2 in r2.iter_lines():
            if name == '' and '<span class="LocationName-geo">' in line2:
                name = line2.split('<span class="LocationName-geo">')[1].split('<')[0]
                days = line2.split("data-days='[")[1].split("}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        if '"intervals":[]' in day:
                            hrs = day.split('"')[0] + ': Closed'
                        else:
                            hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
            if '<meta itemprop="streetAddress" content="' in line2:
                add = line2.split('<meta itemprop="streetAddress" content="')[1].split('"')[0]
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if 'id="telephone">' in line2:
                phone = line2.split('id="telephone">')[1].split('<')[0]
            if '"ids":' in line2:
                store = line2.split('"ids":')[1].split(',')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]            
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
