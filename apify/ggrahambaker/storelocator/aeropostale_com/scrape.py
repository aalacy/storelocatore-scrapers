import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip 
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('aeropostale_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ['us'])

    MAX_RESULTS = 1000
    MAX_DISTANCE = 1000
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    coord = search.next_coord()
    dup_tracker = set()
    all_store_data = []
    base_url = 'https://www.aeropostale.com/storedetails/?StoreID='
    locator_domain = 'https://www.aeropostale.com/'
    while coord:
        x = coord[0]
        y = coord[1]
        url = 'https://www.aeropostale.com/on/demandware.store/Sites-aeropostale-Site/default/Stores-GetNearestStores?latitude=' + str(x) + '&longitude=' + str(y) + '&countryCode=US&distanceUnit=mi&maxdistance=' + str(MAX_DISTANCE)
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)['stores']
        result_coords = []
        
        for num, loc in res_json.items():
            lat = loc['latitude']
            longit = loc['longitude']
            result_coords.append((lat, longit))
            store_number = num
            if store_number not in dup_tracker:
                dup_tracker.add(store_number)
            else:
                continue
                
            location_name = loc['name'].strip()
            street_address = loc['address1'] + ' ' + loc['address2']
            street_address = street_address.strip()
            city = loc['city']
            state = loc['stateCode']
            zip_code = loc['postalCode']
            country_code = 'US'
            
            phone_number = loc['phone'].strip()
            if phone_number == '':
                phone_number = '<MISSING>'
            
            soup = BeautifulSoup(loc['storeHours'], 'html.parser')
            hours = soup.text.replace('Store Hours', '').replace('\n', ' ').strip()
            divs = soup.find_all('div')            

            page_url = base_url + str(store_number)
            
            location_type = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
           
            all_store_data.append(store_data)
        
        if len(res_json) < MAX_RESULTS:
            logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(res_json) == MAX_RESULTS:
            logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()  

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
