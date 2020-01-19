import csv
import os
from sgrequests import SgRequests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

URL = 'https://api.greggs.co.uk/1.0/stores/51.50183269999999/-0.09095100000001821/4000'

session = SgRequests()

HEADERS = {
    'Host': 'api.greggs.co.uk',
    'Origin': 'https://www.greggs.co.uk',
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def fetch_data():
    stores = session.get(URL, headers=HEADERS).json()
    locations = []
    for store in stores:
        locator_domain = 'greggs.co.uk'
        page_url = '<MISSING>'
        location_name = handle_missing(store['name'])
        street_address = handle_missing(store['street'])
        city = handle_missing(store['town'])
        state = '<MISSING>'
        zip_code = handle_missing(store['postcode'])
        country_code = 'GB'
        store_number = handle_missing(store['id'])
        phone = handle_missing(store['phone'])
        location_type = handle_missing(store['type'])
        latitude = handle_missing(store['latitude'])
        if latitude == 0.0:
            latitude = '<MISSING>'
        longitude = handle_missing(store['longitude'])
        if longitude == 0.0:
            longitude = '<MISSING>'
        hours_of_operation = '<MISSING>'
        locations.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
