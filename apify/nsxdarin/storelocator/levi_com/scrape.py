import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('levi_com')



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
    url = 'https://locations.levi.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://locations.levi.com/en-' in line and '.html' in line:
            lurl = line.split('>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'levi.com'
        typ = ''
        hours = ''
        add = ''
        state = ''
        city = ''
        phone = ''
        lat = ''
        lng = ''
        name = ''
        typ = 'Store'
        if '/en-us/' in loc:
            country = 'US'
        else:
            country = 'CA'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        Found = False
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<!-- Desktop schema markup -->' in line2:
                Found = True
            if Found and '"mainEntityOfPage"' in line2:
                Found = False
            if Found and '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
                if 'Outlet' in name:
                    typ = 'Outlet'
                if 'Retail Partner' in name:
                    typ = 'Retail Partner'
            if Found and '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if Found and '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if Found and '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0].strip()
            if Found and '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if Found and '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if Found and '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if Found and '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if Found and '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
        store = loc.replace('.html','').rsplit('_',1)[1]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        name = name.replace('<br/>','')
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
