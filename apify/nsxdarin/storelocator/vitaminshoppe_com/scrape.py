import json
import csv
import urllib2
from sgrequests import SgRequests
import gzip
import os

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
    sitemaps = []
    addinfos = []
    url = 'https://locations.vitaminshoppe.com/sitemap/sitemap_index.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>' in line:
            sitemaps.append(line.split('>')[1].split('<')[0])
    for sm in sitemaps:
        print('Pulling Sitemap %s...' % sm)
        smurl = sm
        with open('branches.xml.gz','wb') as f:
            f.write(urllib2.urlopen(smurl).read())
            f.close()
            with gzip.open('branches.xml.gz', 'rb') as f:
                for line in f:
                    if '<loc>https://locations.vitaminshoppe.com/' in line:
                        lurl = line.split('<loc>')[1].split('<')[0]
                        if '.html' in lurl and '.m.' not in lurl:
                            if lurl not in locs:
                                locs.append(lurl)
        print(str(len(locs)) + ' Locations Found...')
    stores = []
    for loc in locs:
        PFound = True
        while PFound:
            try:
                PFound = False
                r2 = session.get(loc, headers=headers)
                website = 'vitaminshoppe.com'
                name = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                country = 'US'
                store = loc.rsplit('-',1)[1].split('.')[0]
                phone = ''
                lat = ''
                lng = ''
                typ = '<MISSING>'
                hours = ''
                lines = r2.iter_lines()
                for line2 in lines:
                    if '<h2 class="mt-20 mb-20">' in line2:
                        name = line2.split('<h2 class="mt-20 mb-20">')[1].split('<')[0]
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
                    if '"latitude": "' in line2:
                        lat = line2.split('latitude": "')[1].split('"')[0]
                    if '"longitude": "' in line2:
                        lng = line2.split('longitude": "')[1].split('"')[0]
                    if '"openingHours": "' in line2:
                        hours = line2.split('"openingHours": "')[1].split('"')[0]
                if name != '':
                    if phone == '':
                        phone = '<MISSING>'
                    if typ == '':
                        typ = '<MISSING>'
                    addinfo = add + city + state
                    if addinfo not in addinfos and lat != '':
                        addinfos.append(addinfo)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                PFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
