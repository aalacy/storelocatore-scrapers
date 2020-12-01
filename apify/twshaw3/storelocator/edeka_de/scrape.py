import csv
import os
from sgrequests import SgRequests
import sgzip
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('edeka_de')



MAX_RESULTS = 50

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

URL_TEMPLATE = 'https://www.edeka.de/api/marketsearch/markets?searchstring={}&size=' + str(MAX_RESULTS)

search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize(country_codes = ['de'])

session = SgRequests()

HEADERS = {
    'Accept': '*/*',
    'Method': 'GET',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def parse_hours(hours):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return ', '.join(["{}: {}-{}".format(day, hours[day]['from'], hours[day]['to']) for day in days if day in hours])

def fetch_data():
    keys = set()
    locations = []
    postcode = search.next_zip()
    while postcode:
        result_coords = []
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        url = URL_TEMPLATE.format(postcode)
        response = session.get(url, headers=HEADERS).json()
        stores = response["markets"]
        for store in stores:
            latitude = handle_missing(store['coordinates']['lat'])
            longitude = handle_missing(store['coordinates']['lon'])
            result_coords.append((latitude, longitude))
            store_number = handle_missing(store['id'])
            key = store_number
            if key in keys:
                continue
            else:
                keys.add(key)
            locator_domain = 'edeka.de'
            page_url = handle_missing(store['url']) if 'url' in store else '<MISSING>'
            location_name = handle_missing(store['name'])
            address = store['contact']['address']
            street_address = handle_missing(address['street'])
            city = handle_missing(address['city']['name'])
            state = handle_missing(address['federalState'])
            zip_code = handle_missing(address['city']['zipCode'])
            country_code = 'DE'
            phone = handle_missing(store['contact']['phoneNumber'])
            location_type = handle_missing(store['distributionChannel']['name'])
            hours_of_operation = parse_hours(store['businessHours'])
            locations.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
        if len(stores) > 0:
            logger.info(len(stores))
            logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            logger.info("{} zero results!".format(postcode))
        postcode = search.next_zip()
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
