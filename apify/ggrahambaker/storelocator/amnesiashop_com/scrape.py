import csv
from sgrequests import SgRequests
import json

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://amnesiashop.com/apps/api/v1/stores?&_=1575844123335'
    locator_domain = 'https://amnesiashop.com'
    page = session.get(url)
    assert page.status_code == 200

    stores = json.loads(page.content)['stores']

    all_store_data = []
    for store in stores:
        phone_number = store['phone']
        hours_arr = store['open_hours']
        hours = ''
        for h in hours_arr:
            day = h['day']
            open_time = h['open_time']
            close_time = h['close_time']
            
            hours += day + ' ' + open_time + ' : ' + close_time + ' '
            
        addy = store['address']
        location_name = addy['name']
        street_address = addy['line1']  + ' ' + addy['line2'] + ' ' + addy['line3']
        city = addy['city']
        state = addy['state']
        zip_code = addy['zip']
        
        lat = addy['latitude']
        longit = addy['longitude']
        
        country_code = 'CA'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
