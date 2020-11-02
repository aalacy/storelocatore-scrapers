import csv
import requests

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

URL = 'https://members.clubpilates.com/api/brands/clubpilates/locations?geoip=&limit=100000'

def fetch_data():
    locations = []
    response = requests.get(URL)
    stores = response.json()['locations']
    for store in stores:
        if store['coming_soon'] != 'false':
            locator_domain = 'clubpilates.com'
            page_url = handle_missing(store['site_url'])
            location_name = handle_missing(store['name'])
            street_address = handle_missing(store['address'])
            city = handle_missing(store['city'])
            state = handle_missing(store['state'])
            zip_code = handle_missing(store['zip'])
            country_code = handle_missing(store['country_code'])
            store_number = handle_missing(store['seq'])
            phone = handle_missing(store['phone'])
            location_type = '<MISSING>'
            latitude = handle_missing(store['lat'])
            longitude = handle_missing(store['lng'])
            hours_of_operation = '<MISSING>'
            locations.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return locations 

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
