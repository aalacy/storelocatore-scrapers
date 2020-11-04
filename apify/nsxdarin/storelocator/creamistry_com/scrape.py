import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('creamistry_com')

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
    url = 'https://creamistry.com/locations'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'class="stroe_link" href="' in line:
            lurl = 'https://creamistry.com/' + line.split('href="')[1].split('"')[0]
            if 'detail' not in lurl:
                locs.append(lurl)
    logger.info(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        country = ''
        zc = ''
        phone = ''
        logger.info(('Pulling Location %s...' % loc))
        website = 'creamistry.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<h2 class="section-title" style="padding-left:0px !important;">' in line2:
                name = line2.split('<h2 class="section-title" style="padding-left:0px !important;">')[1].split('<')[0]


            if '<h4>Address & Phone</h4>' in line2:
                g = next(lines)
                h = next(lines)
                add = g.split('>')[1].split('<')[0].strip()
                csz = g.split('<br')[1].split('>')[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
                country = 'US'
                phone = h.split('>')[1].split('<')[0]
            if 'var latitude = ' in line2:
                lat = line2.split('var latitude = ')[1].split(';')[0]
            if 'var longitude = ' in line2:
                lng = line2.split('var longitude = ')[1].split(';')[0]
            if 'Store Hours</h4>' in line2:
                g = next(lines)
                h = next(lines)
                if '<p class="mb-0" >' in g:
                    hours = g.split('<p class="mb-0" >')[1].split('</p>')[0].replace('</span>','').replace('</br>',';').replace('  ',' ')
                if '<p class="mb-0" >' in h:
                    hours = hours + '; ' + h.split('<p class="mb-0" >')[1].split('</p>')[0].replace('</span>','').replace('</br>',';').replace('  ',' ')                
        if 'Soon' not in hours:
            if phone == '':
                phone = '<MISSING>'
            hours = hours.replace('<span>','').replace('  ',' ')
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
