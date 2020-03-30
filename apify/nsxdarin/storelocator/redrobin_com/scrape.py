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
    url = 'https://www.redrobin.com/.sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.redrobin.com/locations/' in line:
            items = line.split('<loc>https://www.redrobin.com/locations/')
            for item in items:
                if '</loc>' in item:
                    lurl = 'https://www.redrobin.com/locations/' + item.split('<')[0]
                    if lurl.count('/') == 5:
                        locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'redrobin.com'
        typ = 'Restaurant'
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('<')[0]
            if 'itemprop="streetAddress" class="loc_address">' in line2:
                add = line2.split('itemprop="streetAddress" class="loc_address">')[1].split('<')[0]
            if 'itemprop="addressLocality" class="loc_city">' in line2:
                city = line2.split('itemprop="addressLocality" class="loc_city">')[1].split('<')[0]
            if 'itemprop="addressRegion" class="loc_state">' in line2:
                state = line2.split('itemprop="addressRegion" class="loc_state">')[1].split('<')[0]
            if 'itemprop="postalCode" class="loc_zip">' in line2:
                zc = line2.split('itemprop="postalCode" class="loc_zip">')[1].split('<')[0]
                if ' ' in zc:
                    country = 'CA'
                else:
                    country = 'US'
            if 'class="loc_phone" data-phone="' in line2:
                phone = line2.split('class="loc_phone" data-phone="')[1].split('"')[0]
            if 'data-store-id="' in line2:
                store = line2.split('data-store-id="')[1].split('"')[0]
            if '<time itemprop="openingHours" datetime="' in line2:
                hrs = line2.split('<time itemprop="openingHours" datetime="')[1].split('"')[0].strip()
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '</html>' in line2:
                lat = '<MISSING>'
                lng = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                if hours == '':
                    hours = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
