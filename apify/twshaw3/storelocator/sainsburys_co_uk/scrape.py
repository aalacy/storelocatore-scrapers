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

URL_TEMPLATE = "https://stores.sainsburys.co.uk/api/v1/stores/?fields=slfe-list-2.21&api_client_id=slfe&lat=53.3901702&lon=-1.51136&limit=50&store_type=main%2Clocal&sort=by_distance&within=10000&page={}"

session = SgRequests()

HEADERS = {
    'Authority': 'stores.sainsburys.co.uk',
    'Referer': 'https://stores.sainsburys.co.uk/list/place/@53.3901702,-12.7924904,/1/all',
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def format_hours(hours_json):
    if not hours_json or not len(hours_json) == 7:
        return '<MISSING>'
    DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    parts = []
    for day in hours_json:
        text = ''
        text += DAYS[day['day']] + ': '
        text += day['start_time']
        text += '-'
        text += day['end_time']
        parts.append(text)
    return ', '.join(parts)

def fetch_data():
    locations = []
    page = 1
    while True:
        response = session.get(URL_TEMPLATE.format(page), headers=HEADERS).json()
        page += 1
        stores = response['results']
        if not stores:
            break
        for store in stores:
            locator_domain = 'sainsburys.co.uk'
            page_url = '<MISSING>'
            location_name = handle_missing(store['name'])
            street_address = handle_missing(store['contact']['address1'])
            city = handle_missing(store['contact']['city'])
            state = '<MISSING>'
            zip_code = handle_missing(store['contact']['post_code'])
            country_code = handle_missing(store['contact']['country'])
            country_code = 'GB'
            store_number = store['code']
            phone = handle_missing(store['contact']['telephone'])
            location_type = handle_missing(store['store_type'])
            latitude = handle_missing(store['location']['lat'])
            longitude = handle_missing(store['location']['lon'])
            hours_of_operation = format_hours(store['opening_times'])
            locations.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
