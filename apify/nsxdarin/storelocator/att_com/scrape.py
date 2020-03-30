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
    url = 'https://www.att.com/stores/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.att.com/stores/' in line:
            lurl = line.split('>')[1].split('<')[0]
            count = lurl.count('/')
            if count == 6:
                locs.append(lurl)
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 'att.com'
        typ = 'Store'
        hours = ''
        lat = ''
        name = ''
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
                city = line2.split('<meta itemprop="addressLocality" content="')[1].split('"')[0]
                country = 'US'
                try:
                    state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                except:
                    state = ''
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if name == '' and '"LocationName-brand">' in line2:
                name = line2.split('"LocationName-brand">')[1].split('<')[0].replace('&amp;','&')
            if lat == '' and '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if 'itemprop="telephone" id="telephone">' in line2:
                phone = line2.split('itemprop="telephone" id="telephone">')[1].split('<')[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if 'id="location-name">' not in day:
                        hrs = day.split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if 'puerto-rico/' in loc:
            state = 'PR'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
