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
    urls = ['https://healthy.kaiserpermanente.org/northern-california/facilities/sitemap',
            'https://healthy.kaiserpermanente.org/southern-california/facilities/sitemap',
            'https://healthy.kaiserpermanente.org/colorado-denver-boulder-mountain-northern/facilities/sitemap',
            'https://healthy.kaiserpermanente.org/southern-colorado/facilities/sitemap',
            'https://healthy.kaiserpermanente.org/georgia/facilities/sitemap',
            'https://healthy.kaiserpermanente.org/hawaii/facilities/sitemap',
            'https://healthy.kaiserpermanente.org/maryland-virginia-washington-dc/facilities/sitemap',
            'https://healthy.kaiserpermanente.org/oregon-washington/facilities/sitemap'
            ]
    for url in urls:
        #print(url)
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<loc>https://healthy.kaiserpermanente.org/' in line:
                items = line.split('<loc>https://healthy.kaiserpermanente.org/')
                for item in items:
                    if '<?xml' not in item:
                        lurl = 'https://healthy.kaiserpermanente.org/' + item.split('<')[0]
                        locs.append(lurl)
    print(('Found %s Locations...' % str(len(locs))))
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 'kaiserpermanente.org'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        country = 'US'
        store = loc.rsplit('-',1)[1]
        lat = ''
        lng = ''
        zc = ''
        phone = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if 'phone-number styling-5-marketing" x-ms-format-detection="none">' in line2:
                g = next(lines)
                phone = g.strip().replace('\t','').replace('\r','').replace('\t','')
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('<')[0]
                if ' |' in name:
                    name = name.split(' |')[0]
            if '{"street":"' in line2 and add == '':
                add = line2.split('{"street":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                try:
                    lat = line2.split('"lat":"')[1].split('"')[0]
                    lng = line2.split('"lng":"')[1].split('"')[0]
                except:
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                if ', Suite' in add:
                    add = add.split(', Suite')[0]
                if ' Suite' in add:
                    add = add.split(' Suite')[0]
                if ', Ste' in add:
                    add = add.split(', Ste')[0]
                if ' Ste' in add:
                    add = add.split(' Ste')[0]
            if '<ul class="fd--no-bullets fd--no-padding-margin">' in line2:
                g = next(lines)
                hours = g.split('>')[1].split('<')[0]
                next(lines)
                g = next(lines)
                if 'day' in g and '<li>' in g:
                    hours = hours + '; ' + g.split('>')[1].split('<')[0].strip()
            if '> Holidays' in line2:
                hours = hours + '; ' + line2.split('>')[1].split('<')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        if 'day' not in hours and 'MISSING' not in hours:
            hours = hours + ' - 7 days'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
