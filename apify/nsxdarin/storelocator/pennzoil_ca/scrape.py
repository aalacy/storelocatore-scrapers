import csv
from sgrequests import SgRequests
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pennzoil_ca')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize(country_codes=['ca'])

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locations = []
    coord = search.next_coord()
    while coord:
        llat = coord[0]
        llng = coord[1]
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining())) 
        website = 'pennzoil.ca'
        url = 'https://locator.pennzoil.com/api/v1/pennzoil/oil_change_locations/nearest_to?limit=50&lat=' + str(llat) + '&lng=' + str(llng) + '&format=json'
        r = session.get(url, headers=headers)
        purl = '<MISSING>'
        array = []
        result_coords = []
        for item in json.loads(r.content):
            store = item['id']
            name = item['name']
            lat = item['lat']
            lng = item['lng']
            result_coords.append((lat, lng))
            add = item['address1']
            city = item['city']
            state = item['state']
            zc = item['postcode']
            country = 'CA'
            phone = item['telephone']
            if phone == '':
                phone = '<MISSING>'
            hours = '<MISSING>'
            typ = '<MISSING>'
            canada = ['NL','NS','PE','QC','ON','BC','AB','MB','SK','YT','NU']
            if store not in locations and state in canada:
                locations.append(store)
                if 'PENNZOIL' in name.upper():
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if len(result_coords) > 0:
            search.max_count_update(result_coords)
        else:
            logger.info("zero results")
        coord = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
