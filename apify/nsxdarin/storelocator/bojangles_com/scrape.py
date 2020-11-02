import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bojangles_com')



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
    url = 'https://locations.bojangles.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://locations.bojangles.com/' in line:
            lurl = line.split('>')[1].split('<')[0]
            count = lurl.count('/')
            if count == 5:
                locs.append(lurl)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'bojangles.com'
        typ = 'Restaurant'
        hours = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<span class="LocationName-geo LocationName-geo--noWrap"><span class="LocationName-geomodifier2">' in line2:
                name = line2.split('<span class="LocationName-geo LocationName-geo--noWrap"><span class="LocationName-geomodifier2">')[1].split('</span></span></span>')[0]
                name = name.replace('<span class="LocationName-city">','').replace('</span>','')
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if '<span class="c-address-street-1 ">' in line2:
                add = line2.split('<span class="c-address-street-1 ">')[1].split('<')[0]
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
                country = 'US'
                phone = line2.split('c-phone-main-number-link" href="tel:')[1].split('"')[0]
            if '{"ids":' in line2:
                store = line2.split('{"ids":')[1].split(',')[0]
            if '<div class="Heading Heading--large Nap-hoursToday DottedBottomBorder--redWithPadding"><span class="c-location-hours-today js-location-hours" data-days=\'[' in line2:
                days = line2.split('<div class="Heading Heading--large Nap-hoursToday DottedBottomBorder--redWithPadding"><span class="c-location-hours-today js-location-hours" data-days=\'[')[1].split("]}]'")[0].split('"day":"')
                for day in days:
                    if '"start":' in day:
                        if hours == '':
                            hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        else:
                            hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
