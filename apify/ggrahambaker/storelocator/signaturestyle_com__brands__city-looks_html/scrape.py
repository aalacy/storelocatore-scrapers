import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sgzip import ClosestNSearch

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

    locator_domain = 'https://www.signaturestyle.com/brands/city-looks.html'

    search = ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes = ['us', 'ca'])

    MAX_DISTANCE = 25
    MAX_RESULTS = 50

    coord = search.next_coord()
    all_store_data = []
    dup_tracker = []
    while coord:   
        x = coord[0]
        y = coord[1]

        url = 'https://info3.regiscorp.com/salonservices/siteid/100/salons/searchGeo/map/' + str(x) + '/' + str(y) + '/0.5/0.5/true'
        r = session.get(url, headers=HEADERS)
        res_json = json.loads(r.content)['stores']

        result_coords = []
        
        for loc in res_json:
            lat = loc['latitude']
            longit = loc['longitude']
            result_coords.append((lat, longit))
            
            if loc['actualSiteId'] == 21:
                location_type = 'Best Cuts'
            elif loc['actualSiteId'] == 13:
                location_type = 'BoRics'
            elif loc['actualSiteId'] == 18:
                location_type = 'Famous Hair'
            elif loc['actualSiteId'] == 16:
                location_type = 'Fiesta Salons'
            elif loc['actualSiteId'] == 17:
                location_type = 'Hairmasters'
            elif loc['actualSiteId'] == 15:
                location_type = 'Holiday Hair'
            elif loc['actualSiteId'] == 47:
                location_type = 'Island Haircutting'
            elif loc['actualSiteId'] == 23:
                location_type = 'Saturdays'
            elif loc['actualSiteId'] == 41:
                location_type = 'City Looks'
            elif loc['actualSiteId'] == 22:
                location_type = 'TGF'
            elif loc['actualSiteId'] == 24:
                location_type = 'Head Start'
            elif loc['actualSiteId'] == 7:
                location_type = 'First Choice'
            elif loc['actualSiteId'] == 5:
                location_type = 'Cost Cutters'
            elif loc['actualSiteId'] == 58:
                location_type = 'Chicago Hair'
            elif loc['actualSiteId'] == 14:
                location_type = 'Style America'
            elif loc['actualSiteId'] == 44:
                location_type = 'We Care Hair'
            else:
                location_type = '<MISSING>'
            
            store_number = loc['storeID']
            
            if store_number not in dup_tracker:
                dup_tracker.append(store_number)
            else:
                continue
                
            page_json_url = 'https://info3.regiscorp.com/salonservices/siteid/100/salon/' + str(store_number)
            
            r = session.get(page_json_url, headers=HEADERS)
        
            loc = json.loads(r.content)
            
            location_name = loc['name']
            street_address = loc['address']
            city = loc['city']
            state = loc['state']
            zip_code = loc['zip']
            if len(zip_code.split(' ')) == 2:
                country_code = 'CA'
            else:
                country_code = 'US'
                
            phone_number = loc['phonenumber']
                
            hours_obj = loc['store_hours']
            hours = ''
            for part in hours_obj:
                day = part['days']
                hour_range = part['hours']['open'] + ' - ' + part['hours']['close']
                
                hours += day + ' ' + hour_range + ' '            
            
            if hours == '':
                hours = '<MISSING>'
            
            page_url = '<MISSING>'
            
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
