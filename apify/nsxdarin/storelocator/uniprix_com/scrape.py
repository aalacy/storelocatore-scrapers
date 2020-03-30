import csv
import urllib2
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
    url = 'https://www.uniprix.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.uniprix.com/en/stores/' in line:
            items = line.split('<loc>https://www.uniprix.com/en/stores/')
            for item in items:
                if '<urlset' not in item:
                    lurl = 'https://www.uniprix.com/en/stores/' + item.split('<')[0]
                    locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
        website = 'www.uniprix.com'
        typ = '<INACCESSIBLE>'
        store = '<MISSING>'
        add = ''
        zc = ''
        state = ''
        city = ''
        country = 'CA'
        name = ''
        phone = ''
        hours = ''
        lat = ''
        lng = ''
        lines = r2.iter_lines()
        for line2 in lines:
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if 'itemprop="streetAddress">' in line2:
                g = next(lines)
                h = next(lines)
                if '</a' in g:
                    add = g.split('</a')[0].strip().replace('\t','').replace('<br/>',' ')
                else:
                    add = h.split('</a')[0].strip().replace('\t','').replace('<br/>',' ')
            if 'itemprop="addressLocality">' in line2:
                g = next(lines)
                h = next(lines)
                if '<' in g:
                    city = g.split('  ')[0].replace('\t','').strip()
                    zc = g.split('  ')[1].split('<')[0].strip().replace('\t','')
                else:
                    city = h.split('  ')[0].replace('\t','').strip()
                    zc = h.split('  ')[1].split('<')[0].strip().replace('\t','')
                state = 'Quebec'
            if 'hollow_btn phone" href="tel:' in line2:
                phone = line2.split('hollow_btn phone" href="tel:')[1].split('"')[0]
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-lng="')[1].split('"')[0]
            if '<tr itemprop="openingHours" datetime="' in line2:
                if hours == '':
                    hours = line2.split('<tr itemprop="openingHours" datetime="')[1].split('"')[0]
                else:
                    hours = hours + '; ' + line2.split('<tr itemprop="openingHours" datetime="')[1].split('"')[0]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
