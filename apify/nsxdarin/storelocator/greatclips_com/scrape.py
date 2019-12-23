import csv
import urllib2
import requests

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
    url = 'https://www.greatclips.com/sitemap.GreatClipsSalons.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.greatclips.com/salons/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'greatclips.com'
        typ = 'Salon'
        hours = ''
        country = 'US'
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<span itemprop="name">' in line2:
                name = line2.split('<span itemprop="name">')[1].split('<')[0]
            if '<div class="salon-address">' in line2 and '</div>' in line2 and '<span>' not in line2:
                add = add + ' ' + line2.split('<div class="salon-address">')[1].split('<')[0]
                add = add.strip()
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0].strip()
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0].strip()
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0].strip()
            if '<span itemprop="telephone" content=' in line2:
                phone = line2.split('<span itemprop="telephone" content=')[1].split('">')[1].split('<')[0]
            if '<th scope="row">' in line2:
                day = next(lines).replace('\r','').replace('\n','').replace('\t','').strip()
                next(lines)
                next(lines)
                g = next(lines)
                if '</td>' in g or '<span class="specialHours">' in g:
                    hrs = g.split('<')[0].strip().replace('\t','')
                else:
                    hrs = next(lines).split('<')[0].strip().replace('\t','')
                if hours == '':
                    hours = day + ': ' + hrs
                else:
                    hours = hours + '; ' + day + ': ' + hrs
        lat = '<MISSING>'
        lng = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if ' ' in zc:
            country = 'CA'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
