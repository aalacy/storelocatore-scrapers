import json
import csv
import urllib2
import requests
import gzip
import os

session = requests.Session()
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
    url = 'https://locators.bankofamerica.com/sitemap/sitemap_index.xml'
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
                    if '<loc>https://locators.bankofamerica.com/' in line:
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
                website = 'bankofamerica.com'
                print('Pulling Location %s...' % loc)
                name = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                country = ''
                store = ''
                phone = ''
                lat = ''
                lng = ''
                typ = ''
                hours = ''
                AFound = False
                lines = r2.iter_lines()
                for line2 in lines:
                    if "var fid = '" in line2:
                        store = line2.split("var fid = '")[1].split("'")[0]
                    if '<div class="location-type" aria-label="' in line2:
                        typ = line2.split('<div class="location-type" aria-label="')[1].split('"')[0]
                    if add == '' and '"streetAddress": "' in line2:
                        add = line2.split('"streetAddress": "')[1].split('"')[0]
                    if city == '' and '"addressLocality": "' in line2:
                        city = line2.split('"addressLocality": "')[1].split('"')[0]
                    if state == '' and '"addressRegion": "' in line2:
                        state = line2.split('"addressRegion": "')[1].split('"')[0]
                    if zc == '' and '"postalCode": "' in line2:
                        zc = line2.split('"postalCode": "')[1].split('"')[0]
                    if country == '' and '"@type": "Country",' in line2:
                        country = next(lines).split('"name": "')[1].split('"')[0]
                    if lat == '' and '"latitude": "' in line2:
                        lat = line2.split('"latitude": "')[1].split('"')[0]
                    if lng == '' and '"longitude": "' in line2:
                        lng = line2.split('"longitude": "')[1].split('"')[0]
                    if phone == '' and '"telephone": "' in line2:
                        phone = line2.split('"telephone": "')[1].split('"')[0]
                    if hours == '' and '"openingHours": "' in line2:
                        hours = line2.split('"openingHours": "')[1].split('"')[0].strip()
                    if '"location_name\\": \\"' in line2:
                        name = line2.split('"location_name\\": \\"')[1].split('\\')[0]
                if name != '':
                    if phone == '':
                        phone = '<MISSING>'
                    if typ == '':
                        typ = '<MISSING>'
                    addinfo = add + city + state
                    if addinfo not in addinfos:
                        addinfos.append(addinfo)
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                PFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
