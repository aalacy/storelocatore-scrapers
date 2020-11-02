import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tccrocks_com')



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
    url = 'https://locations.tccrocks.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://locations.tccrocks.com/' in line:
            lurl = line.split('>')[1].split('<')[0]
            count = lurl.count('/')
            if count == 5:
                locs.append(lurl)
    logger.info(('%s Locations Found...' % str(len(locs))))
    for loc in locs:
        #logger.info('Pulling Location %s...' % loc)
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        typ = 'Store'
        hours = ''
        website = 'tccrocks.com'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'kiosk' in line2.lower():
                typ = 'Kiosk'
            if name == '' and '<span class="location-name-brand">' in line2:
                name = line2.split('<span class="location-name-brand">')[1].split('</h1>')[0]
                name = name.replace('<span class="location-name-geo">','').replace('</span>','')
            if 'itemprop="streetAddress"><span class="c-address-street-1">' in line2:
                add = line2.split('itemprop="streetAddress"><span class="c-address-street-1">')[1].split('<')[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
            if phone == '' and 'phone-main-number-link" href="tel:+' in line2:
                phone = line2.split('phone-main-number-link" href="tel:+')[1].split('"')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if hours == '' and "data-days='[{" in line2:
                days = line2.split("data-days='[{")[1].split("}]'")[0].split('"day":"')
                for day in days:
                    if 'intervals' in day:
                        if '"intervals":[]' in day:
                            hrs = day.split('"')[0] + ': Closed'
                        else:
                            hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        hours = hours.replace(': 9',': 09')
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
