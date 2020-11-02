import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shopdisney_com')



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
    states = []
    cities = []
    url = 'https://stores.shopdisney.com/'
    country = 'US'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'CANADA</div>' in line:
            country = 'CA'
        if ' <a linktrack="State index page' in line:
            states.append(line.split('href="')[1].split('"')[0])
    for state in states:
        logger.info(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<a linktrack="City index page' in line2:
                cities.append(line2.split('href="')[1].split('"')[0])
    for city in cities:
        logger.info(('Pulling City %s...' % city))
        r2 = session.get(city, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<a linktrack="Location page' in line2:
                locs.append(line2.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'shopdisney.com'
        typ = ''
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        store = ''
        phone = ''
        lat = ''
        lng = ''
        Found = False
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<meta property="og:url" content="' in line2:
                store = line2.split('<meta property="og:url" content="')[1].split('"')[0].rsplit('/',1)[1]
            if '<meta property="og:title" content="' in line2:
                name = line2.split('<meta property="og:title" content="')[1].split('"')[0]
            if '"@id":"https://stores.shopdisney.com' in line2:
                Found = True
            if Found and '</script>' in line2:
                Found = False
            if '| Toy Store |' in line2:
                typ = line2.split(' in')[0].strip().replace('\t','')
            if Found and '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
            if Found and '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
            if Found and '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if Found and '"addressCountry":"' in line2:
                country = line2.split('"addressCountry":"')[1].split('"')[0]
            if Found and '"latitude":' in line2:
                lat = line2.split('"latitude":')[1].split(',')[0]
            if Found and '"longitude":' in line2:
                lng = line2.split('"longitude":')[1].strip().replace('\r','').replace('\n','').replace('\t','')
            if Found and '"telephone":"' in line2:
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if Found and 'day"' in line2:
                hrs = line2.split('"')[1]
            if Found and '"opens":"' in line2:
                hrs = hrs + ': ' + line2.split('"opens":"')[1].split('"')[0]
            if Found and '"closes":"' in line2:
                hrs = hrs + '-' + line2.split('"closes":"')[1].split('"')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
