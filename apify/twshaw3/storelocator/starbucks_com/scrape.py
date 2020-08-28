import csv
from sgrequests import SgRequests
import sgzip
import datetime
import json
from tenacity import *

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'application/json',
           'x-requested-with': 'XMLHttpRequest'
           }

URL_TEMPLATE = 'https://www.starbucks.com/bff/locations?lat={}&lng={}'
MAX_DISTANCE = 30.0

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['us', 'ca'])

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def parse_hours(store):
    try:
        schedule = store['schedule']
        translate = {}
        day_idx = -1
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'] * 2
        for day in [x['dayName'] for x in schedule] * 2:
            if day_idx == -1 and day in days:
                day_idx = days.index(day)
            if day_idx >= 0:
                translate[day] = days[day_idx]
                day_idx += 1
        day_hours = []
        for day_schedule in schedule:
            day_name = translate.get(day_schedule['dayName'], day_schedule['dayName'])
            times = day_schedule['hours']
            day_hours.append(day_name + ': ' + times)
        hours = ', '.join(day_hours)
        return handle_missing(hours)
    except:
        return '<MISSING>'

def parse(store):
    website = 'starbucks.com'
    store_id = handle_missing(store['storeNumber'])
    name = handle_missing(store['name'])
    phone = handle_missing(store['phoneNumber'])
    lat = handle_missing(store['coordinates']['latitude'])
    lng = handle_missing(store['coordinates']['longitude'])
    add = store['address']['streetAddressLine1']
    try:
        add = add + ' ' + store['address']['streetAddressLine2']
    except:
        pass
    try:
        add = add + ' ' + store['address']['streetAddressLine3']
    except:
        pass
    address = handle_missing(add.strip())
    city = handle_missing(store['address']['city'])
    state = handle_missing(store['address']['countrySubdivisionCode'])
    country = handle_missing(store['address']['countryCode'])
    zc = handle_missing(store['address']['postalCode'])
    typ = handle_missing(store['brandName'])
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    hours = parse_hours(store)
    if country == 'PR':
        country = 'US'
    page_url = '<MISSING>'
    if 'id' in store and 'slug' in store:
        page_url = "starbucks.com/store-locator/store/{}/{}".format(store['id'], store['slug'])
    return [website, page_url, name, add, city, state, zc, country, store_id, phone, typ, lat, lng, hours]

def get_result_coords(stores):
    result_coords = []
    for store in stores:
        result_coords.append((store['coordinates']['latitude'], store['coordinates']['longitude']))
    return result_coords

@retry(stop=stop_after_attempt(10))
def query_locator(query_coord):
    lat, lng = query_coord[0], query_coord[1]
    url = URL_TEMPLATE.format(lat, lng)
    response = session.get(url, headers=HEADERS)
    stores = response.json()['stores']
    return stores

def fetch_data():
    query_coord = search.next_coord()
    locations = []
    ids = set()
    while query_coord:
        print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        stores = query_locator(query_coord)
        if len(stores) == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
            for store in stores:
                store_id = store['storeNumber']
                if store_id not in ids:
                    ids.add(store_id)
                    locations.append(parse(store))
            result_coords = get_result_coords(stores)
            search.max_count_update(result_coords)
        query_coord = search.next_coord()
    for loc in locations:
        yield loc

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
