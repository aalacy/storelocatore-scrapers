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

    locator_domain = 'https://krispykrunchy.com/' 
    ext = 'actions/kkc/locations/locationsGetJson'
    r = session.get(locator_domain + ext, headers = HEADERS)
    loc_json = json.loads(r.content)['locations']

    url_base = 'https://krispykrunchy.com/locations/store-'
    all_store_data = []
    for loc in loc_json:
        
        location_name = loc['title']
        if 'Germantown Gas' in location_name:
            street_address = '<MISSING>'
        else:
            street_address = loc['address']

        city = loc['city']
        state = loc['state']
        if len(state) != 2:
            continue
        zip_code = loc['zip']
        phone_number = loc['phone']
        if phone_number == None:
            phone_number = '<MISSING>'
        store_number = loc['id']
        
        page_url = url_base + store_number
        
        country_code = 'US'
        location_type = '<MISSING>'
        lat = loc['lat']
        if lat == 0:
            lat = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
        longit = loc['lng']
        if longit == 0:
            longit = '<MISSING>'
        if longit == '':
            longit = '<MISSING>'
        
        hours = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
