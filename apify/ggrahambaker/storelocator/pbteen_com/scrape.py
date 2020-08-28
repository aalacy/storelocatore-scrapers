import csv
from sgrequests import SgRequests
import sgzip 
import json

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
    locator_domain = 'https://www.pbteen.com/'

    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ['us', 'ca'])

    MAX_DISTANCE = 100

    coord = search.next_coord()
    all_store_data = []
    dup_tracker = []

    while coord:
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://www.potterybarnkids.com/search/stores.json?brands=PT&lat=' + str(x) + '&lng=' + str(y) + '&radius=' + str(MAX_DISTANCE)
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)['storeListResponse']['stores']

        result_coords = []
        
        for loc in res_json:
            full_loc = loc['properties']
            
            location_name = full_loc['STORE_NAME']
            street_address = full_loc['ADDRESS_LINE_1'] + ' ' + full_loc['ADDRESS_LINE_2']
            street_address = street_address.strip()
            city = full_loc['CITY']
            state = full_loc['STATE_PROVINCE']
            zip_code = full_loc['POSTAL_CODE']
            
            country_code = full_loc['COUNTRY_CODE']
            
            phone_number = full_loc['PHONE_NUMBER_FORMATTED']
            
            store_number = full_loc['STORE_NUMBER']
            if store_number not in dup_tracker:
                dup_tracker.append(store_number)
            else:
                continue
            
            lat = full_loc['LATITUDE']
            longit = full_loc['LONGITUDE']
            
            location_type = full_loc['STORE_TYPE']
            
            hours = full_loc['MONDAY_HOURS_FORMATTED'] + ' ' + full_loc['TUESDAY_HOURS_FORMATTED'] + ' ' + full_loc['WEDNESDAY_HOURS_FORMATTED'] + ' ' 
            hours += full_loc['THURSDAY_HOURS_FORMATTED'] + ' ' + full_loc['FRIDAY_HOURS_FORMATTED'] + ' ' + full_loc['SATURDAY_HOURS_FORMATTED'] + ' ' 
            hours += full_loc['SUNDAY_HOURS_FORMATTED']
            
            page_url = '<MISSING>'
            #'https://www.potterybarn.com/stores/' + country_code.lower() + '/' + state.lower() + '/' + city.lower().replace(' ', '-') + '-' + location_name.strip().lower().replace(' ', '-')
            #print(page_url)
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)

        search.max_distance_update(MAX_DISTANCE)
        coord = search.next_coord()  

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
