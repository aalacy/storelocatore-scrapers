import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import sgzip 

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

    locator_domain = 'https://www.birkenstock.com/'

    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()

    MAX_DISTANCE = 50

    coord = search.next_coord()
    all_store_data = []
    dup_tracker = []
    while coord:
        x = coord[0]
        y = coord[1]
                
        url = 'https://www.birkenstock.com/on/demandware.store/Sites-US-Site/en_US/Stores-GetStoresJson?latitude=' + str(x) + '&longitude=' + str(y) + '&distance=' + str(MAX_DISTANCE) + '&distanceunit=mi&searchText=&countryCode=US&storeLocatorType=regular&storetype1=true'
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)['stores']

        result_coords = []
        result_coords.append((x, y))
        
        for i, loc in res_json.items():
        
            lat = loc['latitude']
            longit = loc['longitude']
            result_coords.append((lat, longit))
            
            if 'BIRKENSTOCK' not in loc['name']:
                continue
                
            location_name = loc['name']
            if location_name not in dup_tracker:
                dup_tracker.append(location_name)
            else:
                continue
            street_address = loc['address1']
            if loc['address2'] != None:
                street_address += ' ' + loc['address2']
            
            city = loc['city']
            state = loc['state']
            zip_code = loc['postalCode']
            country_code = loc['countryCode']
            phone_number = loc['phoneAreaCode'] + ' ' + loc['phone']
            phone_number = phone_number.replace('+1', '').strip()
            
            hours = ''
            
            hours_soup = loc['storeHoursHTML']
            
            cols = BeautifulSoup(hours_soup, 'html.parser').find_all('ul')
            days_li = cols[0].find_all('li')
            hours_li = cols[1].find_all('li')
            hours = ''
            for i, d in enumerate(days_li):
                hours += days_li[i].text + ' ' + hours_li[i].text + ' '
                
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            page_url = '<MISSING>'
            
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
