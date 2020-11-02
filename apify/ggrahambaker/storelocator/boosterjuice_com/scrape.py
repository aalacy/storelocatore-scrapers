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
    url = 'https://www.boosterjuice.com/WebServices/Booster.asmx/StoreLocations'
    r = session.get(url, headers = HEADERS)
    locs = json.loads(r.content)
    locator_domain = 'https://www.boosterjuice.com/'

    all_store_data = []
    for loc in locs:
        store_number = loc['number']
        location_name = loc['name']
        street_address = loc['address'] + ' ' + loc['address2']
        street_address = street_address.strip()
        
        city = loc['city']
        state = loc['province']
        zip_code = loc['postalCode']
        if len(zip_code) == 5:
            continue
        
        country_code = 'CA'
        
        location_type = '<MISSING>'
        
        phone_number = loc['phoneNumber']
        if phone_number == '':
            phone_number = '<MISSING>'
        
        lat = loc['latitude']
        longit = loc['longitude']
        
        if lat == 0:
            lat = '<MISSING>'
        if longit == 0:
            longit = '<MISSING>'
            
        hours = ''
        
        hours_arr = loc['hours']
    
        for day in hours_arr:
            if day['day'] == 'Holidays':
                break
            
            hours += day['day'] + ' '
            
            if day['open'] == None:
                hours += 'Closed '
            else:
                hours += day['open'] + ' '
                hours += day['close'] + ' '
            
        hours = hours.strip()
        if hours == '':
            hours = '<MISSING>'
        
        page_url = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
            
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
