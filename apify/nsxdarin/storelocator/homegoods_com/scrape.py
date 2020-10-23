import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('homegoods_com')



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
    url = 'https://www.homegoods.com/all-stores'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<h5>' in line:
            sname = line.split('<h5>')[1].split('<')[0].strip()
        if '<a class="arrow-link" href="' in line:
            lurl = 'https://www.homegoods.com' + line.split('href="')[1].split('"')[0]
            locs.append(lurl + '|' + sname)
    logger.info(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        logger.info(('Pulling Location %s...' % loc.split('|')[0]))
        website = 'homegoods.com'
        typ = 'Store'
        r2 = session.get(loc.split('|')[0], headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<h2>' in line2:
                g = next(lines)
                h = next(lines)
                add = g.split('<')[0].strip().replace('\t','')
                city = h.split(',')[0].strip().replace('\t','')
                state = h.split(',')[1].strip().split(' ')[0]
                zc = h.rsplit(' ',1)[1].strip().replace('\r','').replace('\n','')
            if '"Phone Number:Call">' in line2:
                phone = line2.split('"Phone Number:Call">')[1].split('<')[0].strip()
                g = next(lines)
                hours = g.split('<')[0].strip().replace('\r','').replace('\n','').replace('\t','')
        country = 'US'
        store = loc.rsplit('/',1)[1]
        lat = '<MISSING>'
        lng = '<MISSING>'
        name = loc.split('|')[1]
        if name == '':
            name = 'Home Goods'
        yield [website, loc.split('|')[0], name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
