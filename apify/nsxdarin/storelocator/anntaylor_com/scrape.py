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
    url = 'https://stores.anntaylor.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://stores.anntaylor.com/' in line:
            lurl = line.split('>')[1].split('<')[0]
            count = lurl.count('/')
            if count == 5 and '/factory/' not in lurl:
                locs.append(lurl)
            if count == 7 and '/factory/' in lurl:
                locs.append(lurl)
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        website = 'anntaylor.com'
        typ = 'Store'
        name = ''
        add = ''
        city = ''
        state = ''
        phone = ''
        zc = ''
        lat = ''
        lng = ''
        country = 'US'
        hours = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'itemprop="name">' in line2:
                name = line2.split('itemprop="name">')[1].split('</h1>')[0].replace('<div>','').replace('</div>','')
                if 'Factory Store' in name:
                    typ = 'Factory Store'
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0].replace(',','')
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                phone = line2.split('itemprop="telephone">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if "data-days='" in line2:
                days = line2.split("data-days='")[1].split("]}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals"' in day:
                        try:
                            hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        except:
                            hrs = day.split('"')[0] + ': Closed'
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        store = '<MISSING>'
        if ' ' in zc:
            country = 'CA'
        if 'M' in zc or 'A' in zc or 'B' in zc:
            country = 'CA'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
