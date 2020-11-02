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

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    
    if state_zip[1] == '':
        state_zip = [state_zip[0], state_zip[2]]
    
    if len(state_zip) == 2:
        state = state_zip[0]
        zip_code = state_zip[1]
        if len(zip_code) > 5:
            country_code = 'CA'
        else:
            country_code = 'US'
        
    elif len(state_zip) == 3:
        state = state_zip[0]
        zip_code = state_zip[1] + ' ' + state_zip[2]
        country_code = 'CA'
    else:
        state = state_zip[0] + ' ' + state_zip[1]
        zip_code = state_zip[2] + ' ' + state_zip[3]
        country_code = 'CA'
        
    return city, state, zip_code, country_code

def fetch_data():
    url = 'https://us.caudalie.com/store-locator/ajax?center_latitude=42.969949561664386&center_longitude=-107.22321733749999&south_west_latitude=13.279324422548623&north_east_latitude=63.09318012402013&south_west_longitude=-158.0679439&north_east_longitude=-56.378490774999996&current_zoom=4&_=1585583274185'
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.caudalie.com/' 
    r = session.get(url, headers = HEADERS)

    locs = json.loads(r.content)
    all_store_data = []
    for loc in locs:
        location_name = loc['label']
        addy = loc['address'].split('<br>')
        if len(addy) > 1:
            street_address = addy[0]
            city, state, zip_code, country_code = addy_ext(addy[1])
        else:
            street_address = loc['address']
            city = '<MISSING>'
            state = '<MISSING>'
            zip_code = '<MISSING>'
        
        if loc['phone_number'] == None:
            phone_number = '<MISSING>'
        else:
            phone_number = loc['phone_number']
           
        lat = loc['latitude']
        longit = loc['longitude']
        
        hours = '<MISSING>'
            
        location_type = loc['cid'].split('_')[0].strip()
        store_number = loc['id']
        
        if location_type == '':
            location_type = '<MISSING>'
        
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
