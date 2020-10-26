import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bedbathandbeyond_com')



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
    url = 'https://stores.bedbathandbeyond.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'Registry</loc>' in line:
            lurl = line.split('<loc>')[1].split('/Registry')[0].replace('&#39;',"'")
            locs.append(lurl)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'bedbathandbeyond.com'
        typ = '<MISSING>'
        hours = ''
        add = ''
        name = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        store = loc.rsplit('-',1)[1]
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if name == '' and 'class="location-name-geo">' in line2:
                name = line2.split('class="location-name-geo">')[1].split('<')[0]
            if add == '' and '<span class="c-address-street-1">' in line2:
                add = line2.split('<span class="c-address-street-1">')[1].split('<')[0]
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                country = 'US'
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
                phone = line2.split('main-number-link" href="tel:')[1].split('">')[1].split('<')[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if '<!doctype html>' not in day:
                        hrs = day.split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('meta itemprop="longitude" content="')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
