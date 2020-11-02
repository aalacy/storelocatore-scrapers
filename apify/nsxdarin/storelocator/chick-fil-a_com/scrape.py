import csv
import os
from sgrequests import SgRequests
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chick-fil-a_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

PATH_TEMPLATE = "/search?q={}&r=1000&per=50"
URL_TEMPLATE = 'https://locator.chick-fil-a.com.yext-cdn.com' + PATH_TEMPLATE

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['us'])

MAX_RESULTS = 50
MAX_DISTANCE = 20

session = SgRequests()

def get_headers(zc):
    return {
        'Authority': 'locator.chick-fil-a.com.yext-cdn.com',
        'Method': 'GET',
        #'Path': PATH_TEMPLATE.format(zc),
        'Scheme': 'https',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        #'Referrer': URL_TEMPLATE.format(zc),
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

COOKIES = {
    'UTMsessionStart': 'true',
    'emHashed': 'undefined',
    '_ga': 'GA1.2.422645551.1582838311',
    '_gid': 'GA1.2.1700769816.1582838311',
    '_mibhv': 'anon-1582838280841-7352020692_8351',
    '_micpn': 'esp:-1::1582838310656',
    '_derived_epik': 'dj0yJnU9QW44aWU5MTl5clNPUUR0TzRvMHpUUjI0eGUwbDBWOHImbj1BZVhNVmVoSC1TSHNWelozaE5VREFRJm09NyZ0PUFBQUFBRjVZTTFB'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def parse_hours(json_hours):
    hours = []
    for day in json_hours:
        if day['isClosed']:
            hours.append("{}: CLOSED".format(day['day']))
        else:
            hours.append("{}: {}-{}".format(day['day'], day['intervals'][0]['start'], day['intervals'][0]['end']))
    return ', '.join(hours)

def fetch_data():
    keys = set()
    coord = search.next_zip()
    while coord:
        result_coords = []
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        r = session.get(URL_TEMPLATE.format(coord), cookies=COOKIES, headers=get_headers(coord)).json()
        stores = r['response']['entities']
        result_coords = []
        for store in stores:
            if 'c_status' in store['profile'] and store['profile']['c_status'].lower() == 'future':
                continue
            address = store['profile']['address']
            city =  address['city']
            state = address['region'] 
            country = address['countryCode']
            website = 'chick-fil-a.com'
            typ = '<MISSING>'
            add = address['line1'] 
            zc = address['postalCode'] 
            name = store['profile']['c_locationName'] 
            store_number = store['profile']['meta']['id'] 
            phone = '<MISSING>'
            if 'mainPhone' in store['profile']:
                phone = store['profile']['mainPhone']['number']
            loc = store['profile']['websiteUrl'] 
            lat = store['profile']['displayCoordinate']['lat'] 
            lng = store['profile']['displayCoordinate']['long']
            yext_lat = store['profile']['yextDisplayCoordinate']['lat']
            yext_lng = store['profile']['yextDisplayCoordinate']['long']
            result_coords.append((yext_lat, yext_lng))
            hours = parse_hours(store['profile']['hours']['normalHours'])
            key = '|'.join([name, add, city, state, zc, country])
            if key not in keys:
                keys.add(key)
                yield [website, loc, name, add, city, state, zc, country, store_number, phone, typ, lat, lng, hours]
        if len(result_coords) > 0:
            search.max_count_update(result_coords)
        else:
            logger.info("max distance update")
            search.max_distance_update(20)
        coord = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
