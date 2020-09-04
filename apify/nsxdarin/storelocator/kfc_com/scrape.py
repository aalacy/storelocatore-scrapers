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
    url = 'https://locations.kfc.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'href="https://locations.kfc.com/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl.count('/') >= 5:
                locs.append(lurl)
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        hours = ''
        add = ''
        lat = ''
        lng = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        country = 'US'
        website = 'kfc.com'
        typ = 'Restaurant'
        store = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        Found = False
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"c_historicStoreID":"' in line2:
                store = line2.split('"c_historicStoreID":"')[1].split('"')[0]
            if '"dimension4":"' in line2:
                name = line2.split('"dimension4":"')[1].split('"')[0]
            if Found is False and '"c-address-street-1">' in line2:
                Found = True
                add = line2.split('"c-address-street-1">')[1].split('<')[0]
                city = line2.split('"c-address-city">')[1].split('<')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                try:
                    phone = line2.split('<div class="Phone-linkWrapper"><a class="Phone-link" href="tel:+1')[1].split('"')[0]
                except:
                    phone = ''
                try:
                    days = line2.split('<div class="Core-secSection-openHours"><span class="c-hours-today js-hours-today" data-days=')[1].split('data-utc')[0].split('"day":"')
                    for day in days:
                        if '"start"' in day:
                            if hours == '':
                                hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                            else:
                                hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                except:
                    hours = '<MISSING>'
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
        if store == '':
            store = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
