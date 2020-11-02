import csv
import requests
import os

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

URL_TEMPLATE = 'https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=stevemadden.myshopify.com&latitude={}&longitude={}&max_distance=0&limit=100000&calc_distance=1'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

session = requests.Session()
proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def fetch_data():
    url = URL_TEMPLATE.format('39.8283', '-98.5795')
    stores = session.get(url, headers=HEADERS).json()['stores']
    locations = []
    keys = set()
    for store in stores:
        if store['country'] not in ['US', 'CA']:
            continue
        locator_domain = 'stevemadden.com'
        page_url = '<MISSING>'
        location_name = handle_missing(store['name'])
        city = handle_missing(store['city'])
        state = handle_missing(store['prov_state'])
        street_address = handle_missing(store['address'])
        if ', {}'.format(state) in street_address:
            street_address = street_address.split(', {}'.format(state))[0]
        zip_code = handle_missing(store['postal_zip'])
        if zip_code != '<MISSING>':
            zip_code = zip_code.rjust(5, '0')
        country_code = handle_missing(store['country'])
        store_number = handle_missing(store['store_id'])
        phone = handle_missing(store['phone'])
        if '/' in phone:
            phone = phone.split('/')[0]
        location_type = '<MISSING>'
        latitude = handle_missing(store['lat'])
        longitude = handle_missing(store['lng'])
        hours_of_operation = handle_missing(store['hours'])
        key = '|'.join([street_address, city, state, zip_code])
        if key in keys:
            continue
        else:
            keys.add(key)
        record = [locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
        locations.append(record)
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
