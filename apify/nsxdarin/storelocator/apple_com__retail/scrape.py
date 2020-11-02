import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('apple_com__retail')



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
    url = 'https://www.apple.com/retail/storelist/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    CFound = True
    for line in r.iter_lines(decode_unicode=True):
        if '<div id="austores"' in line:
            CFound = False
        if '<a href="https://www.apple.com/retail/' in line and '<li>' in line and CFound:
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'apple.com/retail'
        typ = '<MISSING>'
        hours = ''
        name = ''
        city = ''
        add = ''
        zc = ''
        country = 'US'
        state = ''
        store = ''
        phone = ''
        lat = ''
        lng = ''
        fday = ''
        lday = ''
        days = ''
        DFound = False
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '"name": "' in line2 and name == '':
                name = line2.split('"name": "')[1].split('"')[0]
            if '"branchCode": "' in line2:
                store = line2.split('"branchCode": "')[1].split('"')[0]
            if phone == '' and '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
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
            if '"dayOfWeek": [' in line2:
                days = next(lines).split('"')[1]
                DFound = True
            if DFound and ']' in line2:
                DFound = False
            if DFound and 'day"' in line2 and ',' not in line2:
                lday = line2.split('"')[1]
                days = days + '-' + lday
            if '"opens": "' in line2:
                oh = line2.split('"opens": "')[1].split('"')[0]
            if '"closes": "' in line2:
                ch = line2.split('"closes": "')[1].split('"')[0]
                hrs = oh + '-' + ch
                hrs = days + ': ' + hrs
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
