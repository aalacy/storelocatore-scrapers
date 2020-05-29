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

    locator_domain = 'https://www.stevemadden.com/' 
    url = 'https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=stevemadden.myshopify.com&latitude=47.6338217&longitude=-122.3215448&max_distance=100000&limit=300&calc_distance=1'
    r = session.get(url, headers = HEADERS)

    loc_json = json.loads(r.content)
    
    all_store_data = []
    for loc in loc_json['stores']:

        country_code = loc['country']
        if 'US' not in country_code and 'CA' not in country_code:
            continue
        
        location_name = loc['name']
        street_address = loc['address']
        if loc['address2'] != 'NULL':
            street_address += ' ' + loc['address2']
            
        city = loc['city']
        state = loc['prov_state']
        zip_code = loc['postal_zip']
        if zip_code == '':
            zip_code = '<MISSING>'
        phone_number = loc['phone']
        if phone_number == '':
            phone_number = '<MISSING>'
        
        lat = loc['lat']
        longit = loc['lng']
        
        hours = loc['hours']
        if hours == 'NULL' or hours == '':
            hours = '<MISSING>'
        
        page_url = '<MISSING>'
        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
