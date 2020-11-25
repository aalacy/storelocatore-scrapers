import csv
from sgrequests import SgRequests
import sgzip 
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('regalnails_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()

    MAX_RESULTS = 100
    MAX_DISTANCE = 500

    locator_domain = 'https://www.regalnails.com/'

    coord = search.next_coord()
    all_store_data = []
    dup_tracker = []
    while coord:
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://www.regalnails.com/wp-admin/admin-ajax.php?action=store_search&lat=' + str(x) + '&lng=' + str(y) + '&max_results=' + str(MAX_RESULTS) + '&search_radius=' + str(MAX_DISTANCE) + '&filter=10&autoload=1'
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)

        result_coords = []
        
        for loc in res_json:
            location_name = loc['store'].replace('&#038;', '&')
            phone_number = loc['phone']

            page_url = loc['url']
            if page_url == '':
                page_url = '<MISSING>'
            lat = loc['lat']
            longit = loc['lng']
            if phone_number not in dup_tracker:
                dup_tracker.append(phone_number)
                
            else:
                result_coords.append((lat, longit))
                continue

            street_address = loc['address'] + ' ' + loc['address2']
            street_address = street_address.strip()
            
            city = loc['city']
            state = loc['state']
            zip_code = loc['zip']
            if len(zip_code.split(' ')) == 2:
                country_code = 'CA'
            else:
                if len(zip_code) == 6:
                    if '4505 E McKellips Road' in street_address:
                        zip_code = '<MISSING>'
                        country_code = 'US'

                    else:
                        country_code = 'CA'
                        zip_code = zip_code[:3] + ' ' + zip_code[3:]
                else:
                    country_code = 'US'
            
            result_coords.append((lat, longit))
            
            store_number = loc['id'].strip()
            if store_number == '':
                store_number = '<MISSING>'
            
            location_type = '<MISSING>'
            hours = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
        
        if len(res_json) == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
            search.max_count_update(result_coords)
        coord = search.next_coord()  

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
