import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('argos_co_uk')



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
    url = 'https://www.argos.co.uk/stores/#storeslist'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '"azList":[' in line:
            items = line.split('"store_id":"')
            for item in items:
                if '"legacy_name":"' in item:
                    if 'Closed' not in item.split('"legacy_name":"')[1].split('"')[0]:
                        locs.append(item.split('"rel":"ui","href":"')[1].split('"')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'argos.co.uk'
        typ = '<MISSING>'
        hours = ''
        country = 'GB'
        store = ''
        name = ''
        add = ''
        zc = ''
        phone = ''
        state = '<MISSING>'
        city = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"store":{"store"' in line2:
                store = line2.split('"store":{"store"')[1].split('"id":"')[1].split('"')[0]
                add = line2.split('"store":{"store"')[1].split('"address":"')[1].split('"')[0]
                name = line2.split('"store":{"store"')[1].split('"name":"')[1].split('"')[0]
                lat = line2.split('"store":{"store"')[1].split('"lat":')[1].split(',')[0]
                lng = line2.split('"store":{"store"')[1].split('"lng":')[1].split(',')[0]
                city = line2.split('"store":{"store"')[1].split('"town":"')[1].split('"')[0]
                state = '<MISSING>'
                try:
                    zc = line2.split('"store":{"store"')[1].split('"postcode":"')[1].split('"')[0]
                except:
                    zc = '<MISSING>'
                phone = line2.split('"store":{"store"')[1].split('"tel":"')[1].split('"')[0]
                days = line2.split('"storeTimes":[')[1].split(']')[0].split('{"date":"')
                for day in days:
                    if '"time":"' in day:
                        hrs = day.split('"')[0] + ': ' + day.split('"time":"')[1].split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        hours = hours.replace('   -  ',' Closed')
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
