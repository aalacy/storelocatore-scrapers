import csv
from sgrequests import SgRequests
from sgzip import ClosestNSearch
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
    locator_domain = 'https://www.childrensplace.com/'
    search = ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes = ['us', 'ca'])

    MAX_RESULTS = 25
    MAX_DISTANCE = 500

    coord = search.next_coord()
    all_store_data = []
    while coord:
        x = coord[0]
        y = coord[1]
        
        url = "https://www.childrensplace.com/api/v2/store/findStoresbyLatitudeandLongitude"

        HEADERS = {
        "authority": "www.childrensplace.com",
        "method": "GET",
        "path": "/api/v2/store/findStoresbyLatitudeandLongitude",
        "scheme": "https",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-store, must-revalidate",
        "referer": "https://www.childrensplace.com/us/store-locator",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
        "pragma": "no-cache",
        "expires": "0",
        "devictype": "desktop",
        "langid": "-1",
        "storeid": "10151",
        "catalogid": "10551",
        "latitude": str(x),
        "longitude": str(y),
        "maxitems": "1000",
        "radius": "500"
        }

        r = session.get(url, headers=HEADERS)
        

        result_coords = []
        res_json = r.json()['PhysicalStore'][0]
        
        for loc in res_json:
            lat = loc['latitude']
            longit = loc['longitude']
            
            result_coords.append([lat, longit])
            
            
            street_address = loc['addressLine']['0'] + ' ' + loc['addressLine']['1']
            city = loc['city'].strip()
            state = loc['stateOrProvinceName'].strip()
            zip_code = loc['postalCode'].strip()
            country_code = loc['country'].strip()
            
            
            phone_number = loc['telephone1'].strip()
            store_number = loc['storeName']
            
            location_name = loc['description']['displayStoreName']
            
            
            hours_obj = json.loads(loc['attribute']['displayValue'])['storehours']
            hours = ''
            for i, h in enumerate(hours_obj):
                if i == 7:
                    break
                hours += h['nick'] + ' ' + h['availability'][0]['status'] + ' '
            
            
            
            
            location_type = '<MISSING>'
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
