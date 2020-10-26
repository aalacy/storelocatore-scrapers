import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('homedepot_com')



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
    url = 'https://www.homedepot.com/sitemap/d/store.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://www.homedepot.com/l/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        logger.info('Pulling Location %s...' % loc)
        website = 'homedepot.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = ''
        phone = ''
        lat = ''
        lng = ''
        phone = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<h1 class="storeDetailHeader' in line2:
                name = line2.split('<h1 class="storeDetailHeader')[1].split('">')[1].split('<')[0]
            if '"stores":[{' in line2:
                add = line2.split('"street":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                store = line2.split('"storeId":"')[1].split('"')[0]
                lng = line2.split('"lng":')[1].split(',')[0]
                lat = line2.split('"lat":')[1].split('}')[0]
                hours = 'Mon: ' + line2.split('"monday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"monday":{')[1].split('"close":"')[1].split('"')[0]
                hours = hours + '; Tue: ' + line2.split('"tuesday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"tuesday":{')[1].split('"close":"')[1].split('"')[0]
                hours = hours + '; Wed: ' + line2.split('"wednesday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"wednesday":{')[1].split('"close":"')[1].split('"')[0]
                hours = hours + '; Thu: ' + line2.split('"thursday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"thursday":{')[1].split('"close":"')[1].split('"')[0]
                hours = hours + '; Fri: ' + line2.split('"friday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"friday":{')[1].split('"close":"')[1].split('"')[0]
                hours = hours + '; Sat: ' + line2.split('"saturday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"saturday":{')[1].split('"close":"')[1].split('"')[0]
                hours = hours + '; Sun: ' + line2.split('"sunday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"sunday":{')[1].split('"close":"')[1].split('"')[0]
            if '<span itemprop="telephone">' in line2:
                phone = line2.split('<span itemprop="telephone">')[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
