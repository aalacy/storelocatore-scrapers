import csv
from sgrequests import SgRequests
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

    locator_domain = 'https://www.lushusa.com/' 
    ext = 'on/demandware.store/Sites-Lush-Site/default/Stores-FindStores?showMap=false&radius=5000&postalCode=80210'
    r = session.get(locator_domain + ext, headers = HEADERS)

    locs = json.loads(r.content)['stores']

    all_store_data = []
    for loc in locs:
        
        if loc['countryCode'] != 'US':
            continue
            
        store_number = str(loc['ID'])
        page_url = 'https://www.lushusa.com/shop?StoreID=' + store_number
        location_name = loc['name']
        
        street_address = loc['address1']
        if loc['address2'] != None:
            street_address += ' ' + loc['address2']
        
        city = loc['city']
        state = loc['stateCode']
        zip_code = loc['postalCode']
        country_code = loc['countryCode']
        
        lat = loc['latitude']
        longit = loc['longitude']
        if 'phone' not in loc:
            phone_number = '<MISSING>'
        else:
            phone_number = loc['phone']
        
        hours = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
