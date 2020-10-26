import csv
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('plainscapital_com')



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
    url = 'https://www.plainscapital.com/wp-content/themes/plainscapitalbank/core/functions/locationlocator.php?lat=32.7834146&lng=-96.798295&radius=10000&cat=branch'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'link="https://www.plainscapital.com/location/' in line:
            items = line.split('link="https://www.plainscapital.com/location/')
            for item in items:
                if 'lat="' in item:
                    lat = item.split('lat="')[1].split('"')[0]
                    lng = item.split('lng="')[1].split('"')[0]
                    locs.append('https://www.plainscapital.com/location/' + item.split('"')[0] + '|' + lat + '|' + lng)
    for loc in locs:
        logger.info('Pulling Location %s...' % loc.split('|')[0])
        r2 = session.get(loc.split('|')[0], headers=headers)
        website = 'plainscapital.com'
        typ = 'Branch'
        store = '<MISSING>'
        country = 'US'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        xlat = loc.split('|')[1]
        xlng = loc.split('|')[2]
        hours = ''
        HFound = False
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<span itemprop="telephone"' in line2:
                phone = line2.split('tel:')[1].split('"')[0]
            if '"streetAddress">' in line2:
                add = line2.split('"streetAddress">')[1].split('<')[0].strip()
                if ',' in add:
                    add = add.split(',')[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' - ')[0]
            if 'Lobby' in line2 and '<span class="title-underline ">' in line2:
                HFound = True
            if HFound and '<div class="holiday">' in line2:
                HFound = False
            if HFound and ':</div>' in line2:
                day = line2.split('>')[1].split('<')[0]
            if HFound and '<div class="time">' in line2:
                g = next(lines)
                g = str(g.decode('utf-8'))
                if 'Closed' in g:
                    hrs = day + ' Closed'
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
                else:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    ho = g.split('<')[0].strip().replace('\t','')
                    next(lines)
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    hc = g.split('<')[0].strip().replace('\t','')
                    hrs = day + ' ' + ho + '-' + hc
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
        yield [website, loc.split('|')[0], name, add, city, state, zc, country, store, phone, typ, xlat, xlng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
