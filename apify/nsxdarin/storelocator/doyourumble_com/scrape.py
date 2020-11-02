import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('doyourumble_com')



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
    regions = ['12900000001']
    url = 'https://www.doyourumble.com'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<a class="block p-2" href="/returnregion/' in line:
            regions.append(line.split('<a class="block p-2" href="/returnregion/')[1].split('"')[0])
    for region in regions:
        url2 = 'https://www.doyourumble.com/returnregion/' + region
        logger.info(('Pulling Region %s...' % region))
        website = 'doyourumble.com'
        typ = '<MISSING>'
        hours = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = '<MISSING>'
        lat = ''
        lng = ''
        r2 = session.get(url2, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'title: "' in line2:
                name = line2.split('title: "')[1].split('"')[0]
            if 'address1: "' in line2:
                add = line2.split('address1: "')[1].split('"')[0]
            if 'address2: "' in line2:
                csz = line2.split('address2: "')[1].split('"')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
            if 'link: [{"href":"' in line2:
                loc = 'https://www.doyourumble.com/reserve/' + line2.split('reserve\\/')[1].split('"')[0]
            if 'latLng: ["' in line2:
                lat = line2.split('latLng: ["')[1].split('"')[0]
                lng = line2.split('","')[1].split('"')[0]
                if name == 'Upper East Side':
                    names = ['Upper East Side Boxing','Upper East Side Training']
                    for item in names:
                        yield [website, loc, item, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                else:
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
