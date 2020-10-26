import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hearusa_com')



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
    urls = ['https://www.hearusa.com/wpsl_stores-sitemap1.xml','https://www.hearusa.com/wpsl_stores-sitemap2.xml','https://www.hearusa.com/wpsl_stores-sitemap3.xml']
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<loc>https://www.hearusa.com/locations/' in line:
                lurl = line.split('<loc>')[1].split('<')[0]
                if lurl not in locs:
                    locs.append(lurl)
    logger.info(('%s Locations Founds...' % str(len(locs))))
    for loc in locs:
        #logger.info('Pulling Location %s...' % loc)
        website = 'hearusa.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        city = ''
        state = ''
        add = ''
        zc = ''
        country = 'US'
        lat = ''
        phone = ''
        lng = ''
        Found = False
        store = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'enters__header__title">' in line2:
                name = line2.split('enters__header__title">')[1].split('<')[0]
            if '<div class="wpsl-location-address">' in line2:
                addinfo = line2.split('<div class="wpsl-location-address">')[1].split('United States')[0]
                add = addinfo.split('<span>')[1].split('<')[0].strip()
                city = addinfo.split('<span>')[2].split(',')[0].strip()
                state = addinfo.split('<span>')[3].split('<')[0].strip()
                phone = addinfo.split('<span>')[4].split('<')[0].strip()
            if '{"store":"' in line2:
                name = line2.split('{"store":"')[1].split('"')[0]
                add = line2.split('"address":"')[1].split('"')[0]
                try:
                    add = add + ' ' + line2.split('"address2":"')[1].split('"')[0]
                except:
                    pass
                add = add.strip()
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"lng":"')[1].split('"')[0]
                store = line2.split('"id":')[1].split('}')[0]
            if 'Customers: ' in line2:
                phone = line2.split('Customers: ')[1].split('<')[0]
            if '<p>Hours:</p>' in line2:
                Found = True
            if Found and '</div>' in line2:
                Found = False
            if Found and '<p>' in line2 and '!--' not in line2 and 'Hours:' not in line2:
                hrs = line2.split('<p>')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if store == '':
            store = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
            lng = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
