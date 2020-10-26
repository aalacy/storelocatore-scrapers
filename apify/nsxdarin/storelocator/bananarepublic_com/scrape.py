import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bananarepublic_com')



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
    stnames = []
    ids = []
    states = []
    url = 'https://bananarepublic.gap.com/stores/'
    website = 'bananarepublic.com'
    loc = 'https://bananarepublic.gap.com/stores/hi/waipahu/'
    name = 'WAIKELE CENTER'
    add = '94-815a Lumiaina'
    city = 'Waipahu'
    state = 'HI'
    country = 'US'
    phone = '(808) 638-2603'
    hours = 'Mon-Sat: 11:00am - 7:00pm; Sun: 12:00pm - 6:00pm'
    typ = '<MISSING>'
    store = '<MISSING>'
    lat = '21.4007488'
    lng = '-158.001703'
    zc = '96797-5025'
    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<a href="/stores/' in line:
            stname = line.split('<a href="/stores/')[1].split('"')[0]
            if stname not in stnames:
                stnames.append(stname)
                states.append('https://bananarepublic.gap.com/stores/' + stname)
    for state in states:
        cities = []
        logger.info('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<a href="/stores/' in line2:
                cities.append('https://bananarepublic.gap.com' + line2.split('href="')[1].split('"')[0])
        for city in cities:
            locs = []
            logger.info('Pulling City %s...' % city)
            r3 = session.get(city, headers=headers)
            for line3 in r3.iter_lines():
                line3 = str(line3.decode('utf-8'))
                if 'View Store Details</a>' in line3:
                    locs.append('https://bananarepublic.gap.com' + line3.split('href="')[1].split('"')[0])
            for loc in locs:
                logger.info('Pulling Location %s...' % loc)
                website = 'bananarepublic.com'
                typ = '<MISSING>'
                try:
                    store = loc.rsplit('-',1)[1].replace('.html','')
                except:
                    store = '<MISSING>'
                hours = ''
                name = ''
                add = ''
                city = ''
                state = ''
                country = 'US'
                zc = ''
                phone = ''
                lat = ''
                lng = ''
                r4 = session.get(loc, headers=headers)
                lines = r4.iter_lines()
                for line4 in lines:
                    line4 = str(line4.decode('utf-8'))
                    if '<div class="location-name"' in line4:
                        g = next(lines)
                        g = str(g.decode('utf-8'))
                        name = g.split('<')[0].strip().replace('\t','')
                    if '"latitude": "' in line4:
                        lat = line4.split('"latitude": "')[1].split('"')[0]
                    if '"longitude": "' in line4:
                        lng = line4.split('"longitude": "')[1].split('"')[0]
                    if '"openingHours": "' in line4:
                        hours = line4.split('"openingHours": "')[1].split('"')[0].strip()
                    if '"telephone": "' in line4:
                        phone = line4.split('"telephone": "')[1].split('"')[0]
                    if '"streetAddress": "' in line4:
                        add = line4.split('"streetAddress": "')[1].split('"')[0]
                    if '"addressLocality": "' in line4:
                        city = line4.split('"addressLocality": "')[1].split('"')[0]
                    if '"addressRegion": "' in line4:
                        state = line4.split('"addressRegion": "')[1].split('"')[0]
                    if '"postalCode": "' in line4:
                        zc = line4.split('"postalCode": "')[1].split('"')[0]
                if hours == '':
                    hours = '<MISSING>'
                if store not in ids and name != '':
                    ids.append(store)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
