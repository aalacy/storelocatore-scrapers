import csv
import os
from sgrequests import SgRequests
import sgzip
import json

MAX_DISTANCE = 20

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

URL = 'https://www.monoprix.fr/api/graphql?storeInRadiusQuery&cache' 

def get_payload(lat, lng):
    return {"operationName":"storeInRadiusQuery","variables":{"currentLocation":"{},{}".format(lat, lng),"service":[],"storeChain":[],"deliveryTypes":[],"date":[],"__typename":"storeLocatorFilters"},"query":"query storeInRadiusQuery($currentLocation: String!, $service: [String], $storeChain: [String], $deliveryTypes: [String], $date: [String]) {\n  viewer {\n    storesInRadius(currentLocation: $currentLocation, services: $service, storeChaine: $storeChain, deliveryTypes: $deliveryTypes, date: $date, radius: "+str(MAX_DISTANCE)+", isStoreLocator: true) {\n      source {\n        ...StoresMapStoreItemType\n        ...StoreLocatorList\n        store_location\n        sort\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment StoreLocatorList on StoreItemType {\n  store_id\n  store_name\n  street\n  zip_code\n  city\n  seo_url\n  day_0\n  day_0_morning_open_time\n  day_0_morning_close_time\n  day_0_afternoon_open_time\n  day_0_afternoon_close_time\n  day_1\n  day_1_morning_open_time\n  day_1_morning_close_time\n  day_1_afternoon_open_time\n  day_1_afternoon_close_time\n  day_2\n  day_2_morning_open_time\n  day_2_morning_close_time\n  day_2_afternoon_open_time\n  day_2_afternoon_close_time\n  day_3\n  day_3_morning_open_time\n  day_3_morning_close_time\n  day_3_afternoon_open_time\n  day_3_afternoon_close_time\n  day_4\n  day_4_morning_open_time\n  day_4_morning_close_time\n  day_4_afternoon_open_time\n  day_4_afternoon_close_time\n  day_5\n  day_5_morning_open_time\n  day_5_morning_close_time\n  day_5_afternoon_open_time\n  day_5_afternoon_close_time\n  day_6\n  day_6_morning_open_time\n  day_6_morning_close_time\n  day_6_afternoon_open_time\n  day_6_afternoon_close_time\n  __typename\n}\n\nfragment StoresMapStoreItemType on StoreItemType {\n  store_id\n  store_name\n  store_location\n  zip_code\n  street\n  city\n  seo_url\n  __typename\n}\n"}

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['fr'])

session = SgRequests()

HEADERS = {
    'Accept': '*/*',
    'Referer': 'https://www.monoprix.fr/trouver-nos-magasins',
    'Origin': 'https://www.monoprix.fr',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def parse_hours(store):
    ret = []
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for i in range(7):
        op = store['day_{}_morning_open_time'.format(i)]
        cl = store['day_{}_afternoon_close_time'.format(i)]
        day = days[i]
        ret.append("{}: {}-{}".format(day, op, cl))
    return ', '.join(ret)

def km_to_miles(x):
    return x / 1.609344

def fetch_data():
    keys = set()
    locations = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        lat, lng = coord[0], coord[1] 
        response = session.post(URL, json=get_payload(lat, lng), headers=HEADERS).json()
        stores = response["data"]['viewer']['storesInRadius']['source']
        for store in stores:
            lat_lng = store['store_location'].split(',')
            latitude = handle_missing(lat_lng[0])
            longitude = handle_missing(lat_lng[1])
            result_coords.append((latitude, longitude))
            store_number = handle_missing(store['store_id'])
            key = store_number
            if key in keys:
                continue
            else:
                keys.add(key)
            locator_domain = 'monoprix.fr'
            page_url = "{}/{}".format(locator_domain, store['seo_url'])
            location_name = handle_missing(store['store_name'])
            street_address = handle_missing(store['street'])
            city = handle_missing(store['city'])
            state = '<MISSING>' 
            zip_code = handle_missing(store['zip_code'])
            country_code = 'FR'
            phone = '<MISSING>' 
            location_type = '<MISSING>'
            hours_of_operation = parse_hours(store)
            locations.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
        if len(stores) > 0:
            print("max count update")
            search.max_count_update(result_coords)
        else:
            print("max distance update")
            search.max_distance_update(km_to_miles(MAX_DISTANCE))
        coord = search.next_coord()
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
