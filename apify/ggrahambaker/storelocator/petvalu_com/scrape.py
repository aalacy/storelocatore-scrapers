import csv
from sgrequests import SgRequests
import json
import sgzip 
import time
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def unpack(loc):
        locator_domain = 'https://petvalu.com/'
        location_name = loc['na'].replace('&amp;', '&')
        page_url = loc['gu']
        lat = loc['lat']
        longit = loc['lng']
        
        street_address = loc['st'].replace('<br>', ' ').strip()
        zip_code = loc['zp']
        
        city = loc['ct']
        country_code = loc['co'].strip()
        state = loc['rg']
        phone_number = loc['te'].strip()
        
        if phone_number == '':
            phone_number = '<MISSING>'
        else:
            phone_number = re.sub("[^0-9]", "", phone_number)

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'
        
        return [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        
def fetch_data():

    session = SgRequests()
    headers = {'Host': 'us.petvalu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://us.petvalu.com/store-locator/?location=new%20york,&radius=100',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Length': '98',
    'Origin': 'https://us.petvalu.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cookie': 'tk_ai=woo%3ApLgeTii%2Be43iIzeJv3ESzKfM'}

    search = sgzip.ClosestNSearch()
    search.initialize()

    MAX_DISTANCE = 50

    dup_tracker = set()
    coord = search.next_coord()
    all_store_data = []
    while coord:
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        data = { 'lat': str(x), 'lng': str(y), 'action': 'get_stores', 'radius': MAX_DISTANCE }
        
        try:
            r = session.post('https://us.petvalu.com/wp-admin/admin-ajax.php', headers = headers, data = data)
        except:
            print('sleeping:)')
            time.sleep(15)
            print('done')
            r = session.post('https://us.petvalu.com/wp-admin/admin-ajax.php', headers = headers, data = data)

        res_json = json.loads(r.content)

        result_coords = []
        if len(res_json) == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
        
            for k, loc in res_json.items():
                page_url = loc['gu']
                lat = loc['lat']
                longit = loc['lng']
                result_coords.append((lat, longit))

                if page_url not in dup_tracker:
                    dup_tracker.add(page_url)
                else:
                    continue
                
                store_data = unpack(loc)

                all_store_data.append(store_data)

            search.max_count_update(result_coords)
            
        coord = search.next_coord()  

    #### canada 
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ['ca'])

    headers = {'Host': 'petvalu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://petvalu.com/store-locator/?location=toronto,&radius=100',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Length': '99',
    'Origin': 'https://petvalu.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Cookie': 'tk_ai=woo%3ApLgeTii%2Be43iIzeJv3ESzKfM'}

    coord = search.next_coord()
  
    while coord:
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
  
        c_data = { 'lat': str(x), 'lng': str(y), 'action': 'get_stores', 'radius': MAX_DISTANCE }
        try:
            r = session.post('https://petvalu.com/wp-admin/admin-ajax.php', headers = headers, data = c_data)

        except:
            print('sleeping:)')
            time.sleep(15)
            print('done')
            r = session.post('https://petvalu.com/wp-admin/admin-ajax.php', headers = headers, data = c_data)

        res_json = json.loads(r.content)

        result_coords = []
        if len(res_json) == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
        
            for k, loc in res_json.items():
                page_url = loc['gu']
                lat = loc['lat']
                longit = loc['lng']
                result_coords.append((lat, longit))

                if page_url not in dup_tracker:
                    dup_tracker.add(page_url)
                else:
                    continue
                
                store_data = unpack(loc)

                all_store_data.append(store_data)
                
            search.max_count_update(result_coords)

        coord = search.next_coord()

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
