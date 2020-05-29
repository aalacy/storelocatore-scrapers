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
    locator_domain = 'https://www.potbelly.com/'
    
    to_scrape = 'https://api-potbelly-production.fuzzstaging.com/proxy/all-locations'
    page = session.get(to_scrape)

    locs = json.loads(page.content)
    all_store_data = []
    for loc in locs:

        data = loc['location']
        
        hours = data['hours'].replace('\n', ' ')
        lat = data['latitude']
        longit = data['longitude']
        location_name = data['name']
        phone_number = data['phone'].strip()
        if '' == phone_number:
            phone_number = '<MISSING>'
        zip_code = data['postal_code']
        state = data['region']
        city = data['locality']
        street_address = data['street_address'] 
        if data['extended_address'] != None:
            street_address += ' ' + data['extended_address']
        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        page_url = '<MISSING>'
        
        country_code = 'US'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
