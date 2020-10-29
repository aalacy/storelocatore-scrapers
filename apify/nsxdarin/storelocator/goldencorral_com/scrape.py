import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('goldencorral_com')



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
    for x in range(-60, -170, -5):
        for y in range(15, 65, 5):
            lat1 = y
            lat2 = y + 5
            lng1 = x
            lng2 = x + 5
            logger.info((str(lat1) + ',' + str(lng1)))
            url = 'https://www.goldencorral.com/locations/wp-json/locator/v1/search/0/0/' + str(lat1) + '/' + str(lng1) + '/' + str(lat2) + '/' + str(lng2)
            r = session.get(url, headers=headers)
            if r.encoding is None: r.encoding = 'utf-8'
            for item in json.loads(r.content):
                lat = item['lat']
                lng = item['lng']
                name = item['company']
                store = item['customer']
                add = item['address']
                city = item['city']
                state = item['state']
                zc = item['zip']
                phone = item['phone']
                country = 'US'
                hours = ''
                opening_soon = item['opening_soon']
                if opening_soon == '0' and store not in locs:
                    locs.append(store)
                    website = 'goldencorral.com'
                    typ = '<MISSING>'
                    addtext = add.split(' ',1)[1].replace('.','').lower().replace(' ','-')
                    loc = 'https://www.goldencorral.com/locations/location-detail/' + store + '/golden-corral-' + addtext
                    try:
                        r = session.get(loc, headers=headers)
                        if r.encoding is None: r.encoding = 'utf-8'
                        lines = r.iter_lines(decode_unicode=True)
                        for line in lines:
                            if '"dayOfWeek":' in line:
                                g = next(lines)
                                day = g.split('"')[1]
                            if '"opens": "' in line:
                                ot = line.split('"opens": "')[1].split(':00"')[0]
                            if '"closes": "' in line:
                                ct = line.split('"closes": "')[1].split(':00"')[0]
                                hrs = day + ': ' + ot + '-' + ct
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                    except:
                        pass
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
