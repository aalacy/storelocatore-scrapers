import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.dairyqueen.com/us-en/Sitemap/'
    locs = []
    country = 'US'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<h2>AB</h2>' in line:
            country = 'CA'
        if '<li><a href="/us-en/locator/Detail/' in line:
            title = line.split('title="')[1].split('"')[0].replace('&amp;','&')
            locs.append(title + '|' + country + '|' + 'https://www.dairyqueen.com' + line.split('href="')[1].split('"')[0])
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        typ = loc.split('|')[0]
        lurl = loc.split('|')[2]
        country = loc.split('|')[1]
        name = 'Dairy Queen'
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        lat = ''
        lng = ''
        store = lurl.rsplit('/',1)[1]
        website = 'dairyqueen.com'
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        Found = False
        for line2 in lines:
            if '>Hours:</h4>' in line2:
                Found = True
            if Found and '</dl>' in line2:
                Found = False
            if Found and '<dt>' in line2:
                day = line2.split('<dt>')[1].split('<')[0].strip()
            if Found and '<dd>' in line2:
                hrs = line2.split('<dd>')[1].split('<')[0].strip()
                if hours == '':
                    hours = day + ': ' + hrs
                else:
                    hours = hours + '; ' + day + ': ' + hrs
            if '<a href="https://maps.google.com/maps?q=' in line2:
                lat = line2.split('<a href="https://maps.google.com/maps?q=')[1].split(',')[0]
                lng = line2.split('<a href="https://maps.google.com/maps?q=')[1].split(',')[1].split('&')[0]
            if 'itemprop="address"' in line2:
                g = next(lines)
                if '>' in g:
                    add = g.split('>')[1].split('<')[0]
                else:
                    add = next(lines).split('>')[1].split('<')[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if typ == '':
            typ = 'DQ Grill & Chill Restaurant'
        if add != '' and city != 'Nassau':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
