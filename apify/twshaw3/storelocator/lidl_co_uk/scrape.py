import csv
import os
from sgrequests import SgRequests
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lidl_co_uk')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

URL_TEMPLATE = 'https://spatial.virtualearth.net/REST/v1/data/588775718a4b4312842f6dffb4428cff/Filialdaten-UK/Filialdaten-UK?spatialFilter=nearby({},{},1000)&$filter=Adresstyp%20Eq%201&$top=250&$format=json&$skip=0&key=Argt0lKZTug_IDWKC5e8MWmasZYNJPRs0btLw62Vnwd7VLxhOxFLW2GfwAhMK5Xg&Jsonp=displayResultStores'

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['gb'])

MAX_RESULTS = 250

session = SgRequests()

HEADERS = {
    'Accept': '*/*',
    'Method': 'GET',
    'Path': '/REST/v1/data/588775718a4b4312842f6dffb4428cff/Filialdaten-UK/Filialdaten-UK?spatialFilter=nearby(51.5064,-0.1272,1000)&$filter=Adresstyp%20Eq%201&$top=250&$format=json&$skip=0&key=Argt0lKZTug_IDWKC5e8MWmasZYNJPRs0btLw62Vnwd7VLxhOxFLW2GfwAhMK5Xg&Jsonp=displayResultStores',
    'Scheme': 'https',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referrer': 'https://www.lidl.co.uk/about-us/store-finder-opening-hours',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def parse_hours(raw_hours):
    ret = ', '.join(raw_hours.replace('</b>', '<br>').split('<br>')[0:2])
    if ret.endswith(', '):
        ret = ret[0:-2]
    if '<' in ret:
        ret = ret.split('<')[0]
    return handle_missing(ret)

def fetch_data():
    keys = set()
    locations = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        lat, lng = coord[0], coord[1]
        url = URL_TEMPLATE.format(lat, lng)
        response = str(session.get(url, headers=HEADERS).content, 'utf-8')
        l_index = response.find('{')
        r_index = response.rfind('}') + 1
        raw_json = response[l_index:r_index]
        parsed = json.loads(raw_json)
        stores = parsed['d'].get('results', [])
        for store in stores:
            latitude = handle_missing(store['Latitude'])
            longitude = handle_missing(store['Longitude'])
            result_coords.append((latitude, longitude))
            store_number = handle_missing(store['EntityID'])
            key = store_number
            if key in keys:
                continue
            else:
                keys.add(key)
            locator_domain = 'lidl.co.uk'
            page_url = '<MISSING>'
            location_name = handle_missing(store['ShownStoreName'])
            street_address = handle_missing(store['AddressLine'])
            city = handle_missing(store['ShownPostalCode'])
            state = '<MISSING>'
            zip_code = handle_missing(store['PostalCode'])
            country_code = 'GB'
            phone = '<MISSING>'
            location_type = '<MISSING>'
            hours_of_operation = parse_hours(store['OpeningTimes'])
            if 'coming soon' not in  hours_of_operation.lower() and 'under construction' not in hours_of_operation.lower():
                locations.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
        if len(stores) <= MAX_RESULTS:
            logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + MAX_RESULTS + " results")
        coord = search.next_coord()
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
