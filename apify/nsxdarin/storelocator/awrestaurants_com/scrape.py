import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('awrestaurants_com')



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
    url = 'https://awrestaurants.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>http://awdev.dev.wwbtc.com/locations/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'awrestaurants.com'
        typ = 'Restaurant'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        store = '<MISSING>'
        country = 'US'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<div class="hours__row">' in line2:
                g = next(lines)
                hrs = g.replace('</span><span>',': ').replace('<span>','').replace('</span>','').replace('-->','').strip().replace('\t','').replace('\n','').replace('\r','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if 'main-name"><h1>' in line2:
                name = line2.split('main-name"><h1>')[1].split('<')[0]
            if '"store":{"address":"' in line2:
                add = line2.split('"store":{"address":"')[1].split('"')[0]
                city = line2.split(',"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"long":"')[1].split('"')[0]
                try:
                    phone = line2.split(',"phone":"')[1].split('"')[0]
                except:
                    phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
