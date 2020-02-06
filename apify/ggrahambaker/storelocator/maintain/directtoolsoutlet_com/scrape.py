import csv
import requests
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

    locator_domain = 'https://www.directtoolsoutlet.com/'
    ext = 'store-finder?q=&page=0&latitude=19.429620900000003&longitude=-99.1312268'
    print(locator_domain + ext)
    to_scrape = locator_domain + ext
    page = requests.get(to_scrape)
    assert page.status_code == 200

    locs = json.loads(page.content)['data']
    all_store_data = []
    for loc in locs:
        location_name = loc['displayName']
        phone_number = loc['phone']
        street_address = loc['line1']
        if loc['line2'] is not None:
            street_address += ' ' + loc['line2']
        
        city = loc['town']
        zip_code = loc['postalCode']
        lat = loc['latitude']
        longit = loc['longitude']
        state = loc['region']
        
        hours = '<MISSING>'

        
        country_code = 'US'

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
