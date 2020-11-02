import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('onemedical_com')



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
    cities = []
    url = 'https://www.onemedical.com/locations/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<a href="/locations/' in line and 'class="link-list' in line:
            code = line.split('/locations/')[1].split('"')[0]
            lurl = 'https://www.onemedical.com/api/locations/?code=' + code
            logger.info(('Pulling Region %s...' % code))
            r2 = session.get(lurl, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if '"latitude\\": ' in line2:
                    items = line2.split('"latitude\\": ')
                    for item in items:
                        if '"slug\\": \\"' in item:
                            iadd = item.split('"address1\\": \\"')[1].split('\\')[0] + ' ' + item.split('"address2\\": \\"')[1].split('\\')[0]
                            iadd = iadd.strip()
                            ilat = item.split(',')[0]
                            ilng = item.split('\\"longitude\\": ')[1].split(',')[0]
                            locs.append('https://www.onemedical.com/locations/' + code + '/' + item.split('"slug\\": \\"')[1].split('\\')[0] + '|' + ilat + '|' + ilng + '|' + iadd)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc.split('|')[0]))
        website = 'onemedical.com'
        purl = loc.split('|')[0]
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        country = 'US'
        lat = loc.split('|')[1]
        lng = loc.split('|')[2]
        add = loc.split('|')[3]
        store = '<MISSING>'
        hours = ''
        phone = ''
        zc = ''
        r2 = session.get(purl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<title>' in line2 and name == '':
                name = line2.split('<title>')[1].split(' |')[0]
            if '<p itemprop="telephone"><a href="tel:' in line2:
                phone = line2.split('<p itemprop="telephone"><a href="tel:')[1].split('"')[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split('<')[0]
            if 'Office Hours:</h5><div class="rich-text">' in line2:
                hours = line2.split('Office Hours:</h5><div class="rich-text">')[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
