import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('smartstyle_com')



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
    url = 'https://www.smartstyle.com/en-us/salon-directory.html'
    locs = []
    canada = ['ab','nb','on','bc','nl','qc','mb','ns','sk']
    states = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'style="width: 100%; margin-bottom: 10px;" href="' in line:
            states.append(line.split('href="')[1].split('"')[0])
    for state in states:
        logger.info('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<tr><td><a href="' in line2:
                locs.append('https://www.smartstyle.com' + line2.split('href="')[1].split('"')[0])
    logger.info('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = loc.split('.html')[0].rsplit('-',1)[1]
        lat = ''
        lng = ''
        hours = ''
        country = 'US'
        zc = ''
        phone = ''
        HFound = False
        #logger.info('Pulling Location %s...' % loc)
        website = 'smartstyle.com'
        typ = 'Salon'
        PFound = True
        retries = 0
        while PFound:
            try:
                PFound = False
                retries = retries + 1
                r2 = session.get(loc, headers=headers, timeout=5)
                for line2 in r2.iter_lines():
                    line2 = str(line2.decode('utf-8'))
                    if '<meta itemprop="openingHours" content="' in line2:
                        hrs = line2.split('<meta itemprop="openingHours" content="')[1].split('"')[0].strip()
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                    if '<h2 class="hidden-xs salontitle_salonlrgtxt">' in line2:
                        name = line2.split('<h2 class="hidden-xs salontitle_salonlrgtxt">')[1].split('<')[0]
                    if 'var salonDetailLat = "' in line2:
                        lat = line2.split('var salonDetailLat = "')[1].split('"')[0]
                    if 'var salonDetailLng = "' in line2:
                        lng = line2.split('var salonDetailLng = "')[1].split('"')[0]
                    if 'itemprop="streetAddress">' in line2:
                        add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
                    if '<span  itemprop="addressLocality">' in line2:
                        city = line2.split('<span  itemprop="addressLocality">')[1].split('<')[0]
                    if '<span itemprop="addressRegion">' in line2:
                        state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                    if '"postalCode">' in line2:
                        zc = line2.split('"postalCode">')[1].split('<')[0]
                    if 'id="sdp-phn" value="' in line2:
                        phone = line2.split('id="sdp-phn" value="')[1].split('"')[0]
                    if "sc_secondLevel = '/content/smartstyle/www/en-us/locations/" in line2:
                        stabb = line2.split("sc_secondLevel = '/content/smartstyle/www/en-us/locations/")[1].split("'")[0]
                if stabb in canada:
                    country = 'CA'
                if add != '':
                    if phone == '':
                        phone = '<MISSING>'
                    if hours == '':
                        hours = '<MISSING>'
                    state = state.replace('&nbsp;','')
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                if retries <= 3:
                    PFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
