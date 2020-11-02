import csv
from sgrequests import SgRequests
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('longhornsteakhouse_com')



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
    url = 'https://www.longhornsteakhouse.com/locations-sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://www.longhornsteakhouse.com/locations/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        time.sleep(1)
        logger.info('Pulling Location %s...' % loc)
        website = 'longhornsteakhouse.com'
        typ = 'Restaurant'
        hours = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        country = ''
        name = ''
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'id="restLatLong" value="' in line2:
                lat = line2.split('id="restLatLong" value="')[1].split(',')[0]
                lng = line2.split('id="restLatLong" value="')[1].split(',')[1].split('"')[0]
            if '<span id="popRestHrs">' in line2:
                hours = line2.split('<span id="popRestHrs">')[1].split('<br></span>')[0].replace('</span>','').replace('<br>','; ').replace('<span class="times">','').strip()
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if 'id="restAddress" value="' in line2:
                add = line2.split('id="restAddress" value="')[1].split(',')[0]
                city = line2.split('id="restAddress" value="')[1].split(',')[1]
                state = line2.split('id="restAddress" value="')[1].split(',')[2]
                zc = line2.split('id="restAddress" value="')[1].split(',')[3].split('"')[0]
                country = 'US'
            if '"streetAddress":"' in line2:
                if add == '':
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    country = line2.split('"addressCountry":"')[1].split('"')[0]
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                    state = line2.split('"addressRegion":"')[1].split('"')[0]
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                if lat == '':
                    try:
                        lat = line2.split('"latitude":"')[1].split('"')[0]
                        lng = line2.split('"longitude":"')[1].split('"')[0]
                    except:
                        lat = '<MISSING>'
                        lng = '<MISSING>'
                try:
                    hours = line2.split('"openingHours":["')[1].split('"]')[0].replace('","','; ')
                except:
                    pass
            if ',"telephone":"' in line2:
                phone = line2.split(',"telephone":"')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if 'Cincinnati - Eastgate' in name:
            phone = '(513) 947-8882'
        if 'Orchard Park' in name:
            phone = '(716) 825-1378'
        if 'Gainesville' in name:
            phone = '(352) 372-5715'
        if 'Find A R' not in name:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
