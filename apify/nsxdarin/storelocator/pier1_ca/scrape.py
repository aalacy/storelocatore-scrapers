import csv
from sgrequests import SgRequests
import sgzip
import random
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pier1_ca')



random.seed(123) 

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data(search):
    ids = []
    code = search.next_zip()
    logger.info(("code: {}".format(code)))
    locations = []
    while code:
        logger.info(('Pulling Zip Code %s...' % code))
        logger.info(('{} zip codes remaining'.format(search.zipcodes_remaining())))
        query_country = 'ca'
        url = 'https://www.pier1.ca/on/demandware.store/Sites-pier1_intl_ca-Site/en_CA/Stores-FindFromNav?ajax=true&dwfrm_storelocator_postalCode=' + code + '+1A1'
        coords = []
        r = session.get(url, headers=headers)
        if '"stores":' in r.content:
            for item in json.loads(r.content)['stores']:
                store = item['id']
                website = 'pier1.ca'
                name = item['name']
                add = item['address']
                country = 'CA'
                city = item['city']
                state = item['state']
                zc = item['postalcode']
                typ = 'Store'
                phone = item['phone']
                purl = '<MISSING>'
                lat = item['coords']['lat']
                lng = item['coords']['lng']
                hours = item['storeHoursJson'][0]['day'] + ': ' + item['storeHoursJson'][0]['open'] + '-' + item['storeHoursJson'][0]['close']
                try:
                    hours = hours + '; ' + item['storeHoursJson'][1]['day'] + ': ' + item['storeHoursJson'][1]['open'] + '-' + item['storeHoursJson'][1]['close']
                except:
                    pass
                try:
                    hours = hours + '; ' + item['storeHoursJson'][2]['day'] + ': ' + item['storeHoursJson'][2]['open'] + '-' + item['storeHoursJson'][2]['close']
                except:
                    pass
                try:
                    hours = hours + '; ' + item['storeHoursJson'][3]['day'] + ': ' + item['storeHoursJson'][3]['open'] + '-' + item['storeHoursJson'][3]['close']
                except:
                    pass
                try:
                    hours = hours + '; ' + item['storeHoursJson'][4]['day'] + ': ' + item['storeHoursJson'][4]['open'] + '-' + item['storeHoursJson'][4]['close']
                except:
                    pass
                try:
                    hours = hours + '; ' + item['storeHoursJson'][5]['day'] + ': ' + item['storeHoursJson'][5]['open'] + '-' + item['storeHoursJson'][5]['close']
                except:
                    pass
                try:
                    hours = hours + '; ' + item['storeHoursJson'][6]['day'] + ': ' + item['storeHoursJson'][6]['open'] + '-' + item['storeHoursJson'][6]['close']
                except:
                    pass
                hours = hours.replace('Closed-','Closed')
                if store not in ids:
                    ids.append(store)
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if not coords: logger.info(("zip returned no results: {}".format(search.current_zip)))
        search.max_count_update(coords)
        code = search.next_zip()

def scrape():
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes = ['ca'])
    data = fetch_data(search)
    write_output(data)

scrape()
