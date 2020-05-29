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

    locator_domain = 'https://www.redlion.com/americas-best-value-inns-suites' 

    full_list = 'https://www.redlion.com/api/properties/all.js'
    r = session.get(full_list, headers = HEADERS)

    string = str(r.content.decode())

    loc_info = json.loads(string.replace('var hotelsData = ', '').replace(';', '').strip())

    base_url = 'https://www.redlion.com/api/hotels?_format=json&id='
    all_store_data = []
    for loc in loc_info:
    
        info = loc.split(',')
        loc_id = info[2]
        
        r = session.get(base_url + str(loc_id), headers = HEADERS)
        loc_string = str(r.content.decode())
        loc_json = json.loads(loc_string)[0]
        
        if 'Best Value' not in loc_json['Name']:
            continue
            
        location_name = loc_json['Name']
        coords = loc_json['LatLng'].replace('POINT', '').replace('(', '').replace(')', '').strip().split(' ')
        longit = coords[0]
        lat = coords[1]
        store_number = loc_json['Id']
        phone_number = loc_json['Phone']
        
        page_url = loc_json['Path']
        street_address = loc_json['AddressLine1'] + ' ' + loc_json['AddressLine2']
        street_address = street_address.strip()
        state = loc_json['StateProvince']
        city = loc_json['City']
        zip_code = loc_json['PostalCode']
        if 'Canada' in loc_json['Country']:
            country_code = 'CA'
        else:
            country_code = 'US'
            
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
