import csv
from sgrequests import SgRequests
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('burlington_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for code in sgzip.for_radius(200):
        logger.info('Pulling Zip Code %s...' % code)
        url = 'https://www.mapquestapi.com/search/v2/radius?key=Gmjtd|lu6tnu0bn9,85=o5-lw220&origin=' + code + '+US&radius=200&hostedData=mqap.34107_bcf_stores&_=1569251207933'
        r = session.get(url, headers=headers)
        if 'searchResults' in str(r.content.decode('utf-8')):
            array = json.loads(r.content)
            for item in array['searchResults']:
                store = item['name']
                name = 'Burlington Store #' + store
                phone = item['fields']['phone'][:14]
                add = item['fields']['address']
                lat = item['fields']['mqap_geography']['latLng']['lat']
                lng = item['fields']['mqap_geography']['latLng']['lng']
                website = 'burlington.com'
                city = item['fields']['city']
                state = item['fields']['state']
                zc = item['fields']['postal']
                country = 'US'
                typ = 'Store'
                hours = item['fields']['hours1'] + ' ' + item['fields']['hours2'] + ' ' + item['fields']['hours3']
                hours = hours.strip()
                if store not in ids:
                    ids.append(store)
                    if 'Opening' not in hours:
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
