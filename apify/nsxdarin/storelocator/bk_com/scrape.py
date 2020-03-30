import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://locations.bk.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://locations.bk.com/' in line:
            locurl = line.split('<loc>')[1].split('<')[0]
            if 'search.html' not in locurl:
                locs.append(locurl) 
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        website = 'bk.com'
        typ = 'Restaurant'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        Found = False
        for line2 in r2.iter_lines():
            if '<!doctype html>' in line2:
                if '>All Locations in' not in line2:
                    Found = True
                    name = line2.split('<span class="c-bread-crumbs-name">')[1].split('<')[0]
                    add = line2.split('class="c-address-street-1">')[1].split('<')[0]
                    city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                    state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                    zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                    phone = line2.split('id="telephone">')[1].split('<')[0]
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                    hrs = line2.split('Restaurant Hours</h4>')[1].split("}]' data-showOpenToday=")[0]
                    days = hrs.split('"day":"')
                    for day in days:
                        if '"intervals":' in day:
                            if hours == '':
                                try:
                                    hours = day.split('"')[0] + ': ' + day.split(',"start":')[1].split('}')[0] + '-' + day.split('{"end":')[1].split(',')[0]
                                except:
                                    hours = day.split('"')[0] + ': Closed'
                            else:
                                try:
                                    hours = hours + '; ' + day.split('"')[0] + ': ' + day.split(',"start":')[1].split('}')[0] + '-' + day.split('{"end":')[1].split(',')[0]
                                except:
                                    hours = hours + '; ' + day.split('"')[0] + ': Closed'
        if Found:
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
