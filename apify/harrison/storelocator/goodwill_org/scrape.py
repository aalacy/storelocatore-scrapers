import csv
import requests
import sgzip
import os
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('goodwill_org')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'www.goodwill.org',
    'Origin': 'https://www.goodwill.org',
    'Referer': 'https://www.goodwill.org/locator/',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

URL = "https://www.goodwill.org/getLocations.php"

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def get_form_data(lat, lng):
    return {
        'lat': lat,
        'lng': lng,
        'cats': '3,2'
    }

search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
search.initialize()

session = requests.Session()
proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies

MAX_RESULTS = 10

def fetch_data():
    keys = set()
    locations = []
    coord = search.next_coord()
    while coord:
        logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        form_data = get_form_data(coord[0], coord[1])
        stores = session.post(URL, headers=HEADERS, data=form_data).json()
        result_coords = []
        for store in stores:
            store_number = handle_missing(str(store['id']))
            latitude = handle_missing(store['lat'])
            longitude = handle_missing(store['lng'])
            result_coords.append((latitude, longitude))
            street_address = handle_missing(store['address1'])
            city = handle_missing(store['city'])
            state = handle_missing(store['state'])
            zip_code = handle_missing(store['postal_code'])
            key = store_number 
            if key not in keys:
                keys.add(key)
                locator_domain = 'goodwill.org'
                country_code = store['country']
                location_name = handle_missing(store['name'])
                location_type = handle_missing(store['services'])
                page_url = handle_missing(store['website'])
                if '.org' not in page_url:
                    page_url = '<MISSING>'
                phone = handle_missing(store['phone'])
                hours_of_operation = '<INACCESSIBLE>' 
                record = [locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]
                locations.append(record)
        if len(stores) == MAX_RESULTS:
            logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected " + MAX_RESULTS + " results")
        coord = search.next_coord()
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
