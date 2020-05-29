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
    url = 'https://cdn.shopify.com/s/files/1/1921/1117/t/324/assets/sca.storelocatordata.json'
    locator_domain = 'https://scandinaviandesigns.com/'
    page = session.get(url)
    assert page.status_code == 200
    
    locs = json.loads(page.content)

    all_store_data = []
    for loc in locs:
        lat = loc['lat']
        longit = loc['lng']
        hours = loc['schedule'].replace('<br>', ' ')
        if 'Now Closed' in hours:
            continue

        if 'Soon' in hours:
            continue
            
        location_name = loc['name']
        phone_number = loc['phone']
        page_url = loc['web']
        
        street_address = loc['address']
        state = loc['state']
        city = loc['city']
        zip_code = loc['postal']
        
        country_code = 'US'

        location_type = '<MISSING>'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
