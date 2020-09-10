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
    url = 'https://stores.rue21.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://stores.rue21.com/' in line:
            lurl = line.split('>')[1].split('<')[0]
            count = lurl.count('/')
            if count == 5:
                locs.append(lurl)
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 'rue21.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        store = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if name == '' and '<span class="location-geomodifier">' in line2:
                name = line2.split('<span class="location-geomodifier">')[1].split('<')[0]
            if add == '' and '<span class="c-address-street-1">' in line2:
                add = line2.split('<span class="c-address-street-1">')[1].split('<')[0].strip()
                if '<span class="c-address-street-2">' in line2.split('<span class="c-address-street-1">')[1].split('<span class="c-address-city">')[0]:
                    add = add + ' ' + line2.split('<span class="c-address-street-2">')[1].split('<')[0].strip()
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0].strip()
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
            if 'phone-main-number-link" href="tel:+' in line2:
                phone = line2.split('phone-main-number-link" href="tel:+')[1].split('"')[0]
            if "'ids': " in line2:
                store = line2.split("'ids': ")[1].split(',')[0]
            if hours == '' and "data-days='[{" in line2:
                days = line2.split("data-days='[{")[1].split(']}]')[0].split('"day":"')
                for day in days:
                    if 'intervals' in day:
                        if '"intervals":[{' not in day:
                            hrs = day.split('"')[0] + ': Closed'
                        else:
                            hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
