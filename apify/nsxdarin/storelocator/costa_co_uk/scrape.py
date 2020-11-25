import csv
import os
from sgrequests import SgRequests
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('costa_co_uk')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize(country_codes = ['gb'])

MAX_RESULTS = 250

session = SgRequests()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
           }

def fetch_data():
    ids = []
    adds = []
    locations = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        logger.info(("remaining zipcodes: " + str(search.zipcodes_remaining())))
        x, y = coord[0], coord[1]
        url = 'https://www.costa.co.uk/api/locations/stores?latitude=' + str(x) + '&longitude=' + str(y) + '&maxrec=500'
        r = session.get(url, headers=headers)
        try:
            for item in json.loads(r.content)['stores']:
                store = item['storeNo8Digit']
                typ = item['storeType']
                phone = item['telephone']
                add = item['storeAddress']['addressLine1']
                add = add + ' ' + item['storeAddress']['addressLine2'] + ' ' + item['storeAddress']['addressLine3']
                add = add.strip()
                name = item['storeNameExternal']
                if name == '':
                    name = typ
                city = item['storeAddress']['city']
                state = '<MISSING>'
                zc = item['storeAddress']['postCode']
                country = 'GB'
                lng = item['longitude']
                website = 'costa.co.uk'
                lat = item['latitude']
                hours = 'Mon: ' + item['storeOperatingHours']['openMon'] + '-' + item['storeOperatingHours']['closeMon']
                hours = hours + '; Tue: ' + item['storeOperatingHours']['openTue'] + '-' + item['storeOperatingHours']['closeTue']
                hours = hours + '; Wed: ' + item['storeOperatingHours']['openWed'] + '-' + item['storeOperatingHours']['closeWed']
                hours = hours + '; Thu: ' + item['storeOperatingHours']['openThu'] + '-' + item['storeOperatingHours']['closeThu']
                hours = hours + '; Fri: ' + item['storeOperatingHours']['openFri'] + '-' + item['storeOperatingHours']['closeFri']
                hours = hours + '; Sat: ' + item['storeOperatingHours']['openSat'] + '-' + item['storeOperatingHours']['closeSat']
                hours = hours + '; Sun: ' + item['storeOperatingHours']['openSun'] + '-' + item['storeOperatingHours']['closeSun']
                if ':' not in hours:
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                if add == '':
                    add = '<MISSING>'
                if city == '':
                    city = '<MISSING>'
                loc = '<MISSING>'
                addinfo = add + city + zc
                if 'Mon: -; Tue: -; Wed: -; Thu: -; Fri: -; Sat: -; Sun: -' in hours:
                    hours = '<MISSING>'
                if store not in ids and addinfo not in adds:
                    adds.append(addinfo)
                    ids.append(store)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass
        logger.info("max count update")
        search.max_count_update(result_coords)
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
