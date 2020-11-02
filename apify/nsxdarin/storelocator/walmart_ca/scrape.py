import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('walmart_ca')



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
    url = 'https://www.walmart.ca/sitemap-stores-en.xml'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://www.walmart.ca/en/stores-near-me/' in line and '-only' not in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    logger.info(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = loc.rsplit('-',1)[1]
        lat = ''
        lng = ''
        hours = ''
        country = 'CA'
        zc = ''
        phone = ''
        logger.info(('Pulling Location %s...' % loc))
        website = 'walmart.ca'
        typ = 'Store'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '"dayOfWeek": [' in line2:
                g = next(lines)
                day = g.split('"')[1]
                next(lines)
                g = next(lines)
                h = next(lines)
                hrs = day + ': ' + g.split('"')[3] + '-' + h.split('"')[3]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"latitude": ' in line2:
                lat = line2.split('"latitude": ')[1].split(',')[0]
            if '"longitude": ' in line2:
                lng = line2.split('"longitude": ')[1].replace('\t','').replace('\r','').replace('\n','').strip()
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
        if 'Supercentre' in name:
            typ = 'Supercentre'
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
