import csv
from sgrequests import SgRequests
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dallasbbq_com')



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
    url = 'https://www.dallasbbq.com'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    Found = True
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'Order Online</a></li>' in line:
            Found = False
        if Found and '<a href="https://www.dallasbbq.com/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    logger.info('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        logger.info('Pulling Location %s...' % loc)
        website = 'dallasbbq.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        Found = False
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<a href="tel:' in line2 and 'day' not in line2 and 'Hours' not in line2:
                phone = line2.split('<a href="tel:')[1].split('>')[1].split('<')[0]
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if '<h3 class="title text-cursive" style="text-align: center;"><strong>' in line2 or '<h3><strong>' in line2 and 'tel:' not in line2:
                add = line2.split('<strong>')[1].split('<')[0]
                g = next(lines)
                g = str(g.decode('utf-8')).replace('</strong>','').replace('<strong>','')
                csz = g.split('<')[0].replace('(','').replace(')','')
                if ', ' in csz:
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.split(',')[1].strip().split(' ')[1]
                else:
                    city = '<MISSING>'
                    state = '<MISSING>'
                    zc = '<MISSING>'
            if 'Store Hours:' in line2 and '<strong>' in line2:
                Found = True
            if Found and '<span' in line2:
                Found = False
            if Found and '</div>' in line2:
                Found = False
            if Found and '</p>' in line2 and '<strong>' not in line2:
                hrs = line2.split('</p>')[0].replace('<p>','').replace('<p class="p1">','').replace('&#8211;','-').replace('&amp;','&')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if Found and '<br' in line2 and '<strong>' not in line2:
                hrs = line2.split('<br')[0].replace('<p>','').replace('<p class="p1">','').replace('&#8211;','-').replace('&amp;','&')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        country = 'US'
        store = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        purl = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        cleanr = re.compile('<.*?>')
        hours = re.sub(cleanr, '', hours)
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
