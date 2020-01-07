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
    print('Pulling Sitemap %s...')
    smurl = 'http://www.merlenormanstudio.com/sitemap.xml.gz'
    with open('branches.xml.gz','wb') as f:
        f.write(urllib2.urlopen(smurl).read())
        f.close()
        with gzip.open('branches.xml.gz', 'rb') as f:
            for line in f:
                if '/mn-' in line:
                    lurl = line.split('<loc>')[1].split('<')[0]
                    locs.append(lurl)
    print(str(len(locs)) + ' Locations Found...')
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        website = 'merlenorman.com'
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
        lines = r2.iter_lines()
        Found = False
        for line2 in lines:
            if '"@context":"http://schema.org",' in line2:
                Found = True
            if Found and '</script>' in line2:
                Found = False
            if '"@id":"' in line2 and Found:
                store = line2.split('"@id":"')[1].split('"')[0]
            if '"@type":"' in line2 and Found and typ == '':
                typ = line2.split('"@type":"')[1].split('"')[0]
            if '"name": "' in line2 and Found:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"streetAddress":"' in line2 and Found:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
            if '"addressLocality":"' in line2 and Found:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '"addressRegion":"' in line2 and Found:
                state = line2.split('"addressRegion":"')[1].split('"')[0]
            if '"postalCode":"' in line2 and Found:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"addressCountry":"' in line2 and Found:
                country = line2.split('"addressCountry":"')[1].split('"')[0]
            if '"latitude":' in line2 and Found:
                lat = line2.split('"latitude":')[1].split(',')[0]
            if '"longitude":' in line2 and Found:
                lng = line2.split('"longitude":')[1].replace('\r','').replace('\t','').strip()
            if '"telephone":"' in line2 and Found:
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if 'day"' in line2 and Found:
                hrs = line2.split('"')[1]
            if '"opens":"' in line2 and Found:
                hrs = hrs + ': ' + line2.split('"opens":"')[1].split('"')[0]
            if '"closes":"' in line2 and Found:
                hrs = hrs + '-' + line2.split('"closes":"')[1].split('"')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if state == '' and '<a linktrack="State index page' in line2:
                state = line2.split('(')[1].split(')')[0]
        if '0' not in hours:
            hours = '<MISSING>'
        hours = hours.replace('CLOSED-CLOSED','CLOSED')
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
