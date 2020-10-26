import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('aspencreekgrill_com')



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
    url = 'https://aspencreekgrill.com/'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    Found = False
    for line in r.iter_lines(decode_unicode=True):
        if '<ul class="sub-menu">' in line and len(locs) == 0:
            Found = True
        if Found and 'Menus</a>' in line:
            Found = False
        if Found and 'href="https://aspencreekgrill.com/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    logger.info(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        country = ''
        zc = ''
        phone = ''
        logger.info(('Pulling Location %s...' % loc))
        website = 'aspencreekgrill.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<div class="et_pb_text_inner"><h2>' in line2 and name == '':
                name = line2.split('<div class="et_pb_text_inner"><h2>')[1].split('<')[0]
                state = next(lines).split('>')[1].split('<')[0]
            if 'Address</span></h4>' in line2:
                g = next(lines).replace('<span>','').replace('</span>','')
                if '<p>' in g:
                    add = g.split('<p>')[1].split('<')[0]
                    city = g.split('<br />')[1].split(',')[0].strip()
                    zc = g.split('</p>')[0].rsplit(' ',1)[1]
                else:
                    add = g.split('">')[1].split('<')[0]
                    g = next(lines)
                    city = g.split(',')[0]
                    zc = g.split('<')[0].rsplit(' ',1)[1]
                country = 'US'
                store = '<MISSING>'
            if 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0]
            if 'Hours</span></h4>' in line2:
                g = next(lines)
                if '<p>' in g:
                    hours = g.split('<p>')[1].split('</p>')[0].replace('<br />','; ')
                else:
                    hours = g.split('">')[1].split('<')[0]
                    hours = hours + '; ' + next(lines).split('<')[0].strip()
            if 'CALL AHEAD:' in line2:
                phone = line2.split('CALL AHEAD:')[1].split('<')[0].strip()
        if '<' in zc:
            zc = zc.split('<')[0]
        hours = hours.replace('&amp;','&').replace('&#8211;','-')
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
