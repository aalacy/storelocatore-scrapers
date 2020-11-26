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

    locator_domain = 'https://www.americastire.com'
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()

    MAX_DISTANCE = 25

    store_ids = set()
    zip_code = search.next_zip()
    all_store_data = []
    dup_counter = []
    while zip_code:        
        url = 'https://www.americastire.com/store-locator/findStores?q=' + str(zip_code) + '&max=75'
        new_zips = [str(zip_code)] 
        
        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)

        if res_json['results'] == None:
            search.max_distance_update(MAX_DISTANCE)
            zip_code = search.next_zip()
            continue
        
        for loc in res_json['results']:
    
            lat = loc['geoPoint']['latitude']
            longit = loc['geoPoint']['longitude']
            
            location_name = loc['displayName']
            page_url = 'https://www.discounttire.com' + loc['url']
            if page_url not in dup_counter:
                dup_counter.append(page_url)
            else:
                continue
            
            addy = loc['address']
            
            street_address = addy['line1'] 
    
            if addy['line2'] != None:
                street_address += ' ' + addy['line2']
                
            city = addy['town']
            state = addy['region']['name']
            country_code = addy['region']['countryIso']
            
            zip_code = addy['postalCode'].split('-')[0]
            
            phone_number = addy['phone']
            
            hours = ''
            for h in loc['openingHours']['weekDaysList']:
                start = h['openingTime']['formattedHour']
                end = h['closingTime']['formattedHour']
                
                day = h['dayOfWeek']
                
                if start == None:
                    hours += day + ' Closed' + ' '
    
                else:
                    hours += day + ' ' + str(start) + ' ' + str(end) + ' '
                
            hours = hours.strip()
            
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)
            
        search.max_distance_update(MAX_DISTANCE)
        zip_code = search.next_zip()
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
