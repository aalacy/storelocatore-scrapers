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
    locator_domain = 'https://www.take5oilchange.com'
    search = ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()

    MAX_DISTANCE = 50
    all_store_data = []
    coord = search.next_zip()
    dup_tracker = set()
    while coord:
        url = 'https://www.take5oilchange.com/api/stores/search/' + str(coord)
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)['results']

        result_coords = []
        
        for loc in res_json:
            if loc['IsUpcomingStore']:
                continue
        
            street_address = loc['Location_Address']
            city = loc['Location_City']
            state = loc['Location_State']
            
            zip_code = loc['Location_PostalCode']
            store_number = loc['License_Number']
            
            if store_number not in dup_tracker:
                dup_tracker.add(store_number)
            else:
                continue
            
            longit = loc['Location_Longitude']
            lat = loc['Location_Latitude']
            
            if 'Organic_Call_Tracking_Number' in loc:
                phone_number = loc['Organic_Call_Tracking_Number']
            else:
                phone_number = '<MISSING>'

            location_name = loc['Center_Name']
            
            result_coords.append((lat, longit))
        
            country_code = 'US'
            location_type = '<MISSING>'
            
            hours = 'Monday ' + loc['Monday_Open'] + ' - ' + loc['Monday_Close'] + ' '
            hours += 'Tuesday ' + loc['Tuesday_Open'] + ' - ' + loc['Tuesday_Close'] + ' '
            hours += 'Wednesday ' + loc['Wednesday_Open'] + ' - ' + loc['Wednesday_Close'] + ' '
            hours += 'Thursday ' + loc['Thursday_Open'] + ' - ' + loc['Thursday_Close'] + ' '
            hours += 'Friday ' + loc['Friday_Open'] + ' - ' + loc['Friday_Close'] + ' '
            hours += 'Saturday ' + loc['Saturday_Open'] + ' - ' + loc['Saturday_Close'] + ' '
            
            if 'Closed' in loc['Sunday_Open']:
                hours += 'Sunday Closed'
            else:
                hours += 'Sunday ' + loc['Sunday_Open'] + ' - ' + loc['Sunday_Close'] + ' '
                
            page_url = '<MISSING>'
                
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
        
        if len(res_json) == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
            search.max_count_update(result_coords)
        
        coord = search.next_zip()  

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
