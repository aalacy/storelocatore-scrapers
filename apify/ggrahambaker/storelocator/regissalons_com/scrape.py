import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import sgzip 
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('regissalons_com')



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
    locator_domain = 'https://www.regissalons.com/'
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ['ca', 'us'])

    MAX_RESULTS = 25
    MAX_DISTANCE = 500

    coord = search.next_coord()
    all_store_data = []

    dup_tracker = []

    while coord:
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://www.regissalons.com/wp-admin/admin-ajax.php?action=store_search&lat=' + str(x) + '&lng=' + str(y) + '&max_results=' + str(MAX_RESULTS) + '&search_radius=' + str(MAX_DISTANCE) 
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)

        result_coords = []
        result_coords.append((x, y))
  
        for loc in res_json:
            lat = loc['lat']
            longit = loc['lng']
            result_coords.append((lat, longit))
            
            location_name = loc['store'].replace('&#8211;', '').replace('&#8217;', "'").replace('&#038;', '&')
           
            phone_number = loc['phone']
            if phone_number not in dup_tracker:
                dup_tracker.append(phone_number)
            else:
                continue

            street_address = loc['address2']
            city = loc['city']
            state = loc['state']
            zip_code = loc['zip']

            if len(zip_code.split(' ')) == 2:
                country_code = 'CA'
            else:
                country_code = 'US'
            
            store_number = loc['id']
            
            hours_obj = loc['hours']
            
            soup = BeautifulSoup(hours_obj, 'html.parser')
            
            hours_table = soup.find_all('tr')
            hours = ''
            for row in hours_table:
                tds = row.find_all('td')
                for td in tds:
                    hours += td.text + ' '

            page_url = loc['permalink']
            
            location_type = '<MISSING>'
            
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
