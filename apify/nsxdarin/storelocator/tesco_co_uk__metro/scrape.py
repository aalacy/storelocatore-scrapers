import csv
import os
from sgrequests import SgRequests
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

URL_TEMPLATE = 'https://api.tesco.com/tescolocation/v3/locations/search?offset=0&limit=100&sort=near:%22{},{}%22&filter=category:Store%20AND%20isoCountryCode:x-uk&fields=name,geo,openingHours,altIds.branchNumber,contact'

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['gb'])

MAX_RESULTS = 100

session = SgRequests()

HEADERS = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'api.tesco.com',
    'Origin': 'https://www.tesco.com',
    'Referrer': 'https://www.tesco.com/store-locator/uk/?address=IV1',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'TraceId': '2e42a7b5-0334-46fc-9dba-67a995551f77',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
    'X-AppKey': 'store-locator-web-cde'
}

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def parse_hours(json_hours):
    trading_hours_list = [x for x in json_hours if x['type'] == 'Trading']
    if len(trading_hours_list) == 0:
        return '<MISSING>'
    trading_hours = trading_hours_list[0]
    if 'standardOpeningHours' not in trading_hours:
        return '<MISSING>'
    hours_list = trading_hours['standardOpeningHours']
    parts = []
    DAYS = {'mo': 'Monday', 'tu': 'Tuesday', 'we': 'Wednesday', 'th': 'Thursday', 'fr': 'Friday', 'sa': 'Saturday', 'su': 'Sunday'}
    for day in DAYS.keys():
        text = ''
        text += DAYS[day]
        text += ': '
        if hours_list[day]['isOpen'] == 'true':
            if 'open' not in hours_list[day]:
                text += '24 hours'
            else:
                text += hours_list[day]['open']
                text += '-'
                if 'close' not in hours_list[day]:
                    text += 'Midnight'
                else:
                    text += hours_list[day]['close']
        else:
            text += 'Closed'
        parts.append(text)
    return ', '.join(parts)

def fetch_data():
    keys = set()
    locations = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        lat, lng = coord[0], coord[1]
        url = URL_TEMPLATE.format(lat, lng)
        response = session.get(url, headers=HEADERS).json()
        stores = [result['location'] for result in response.get('results', [])]
        for store in stores:
            latitude = handle_missing(store['geo']['coordinates']['latitude'])
            longitude = handle_missing(store['geo']['coordinates']['longitude'])
            result_coords.append((latitude, longitude))
            store_number = handle_missing(store['altIds']['branchNumber'])
            key = store['id']
            if key in keys:
                continue
            else:
                keys.add(key)
            locator_domain = 'tesco.com'
            page_url = '<MISSING>'
            location_name = handle_missing(store['name'])
            address1_list = [x for x in store['contact']['address']['lines'] if x['lineNumber'] == 1]
            street_address = '<MISSING>'
            if len(address1_list) > 0:
                street_address = handle_missing(address1_list[0]['text'])
            city = handle_missing(store['contact']['address']['town'])
            state = '<MISSING>'
            zip_code = handle_missing(store['contact']['address']['postcode'])
            country_code = 'GB'
            phone = '<MISSING>'
            if 'phoneNumbers' in store['contact'] and len(store['contact']['phoneNumbers']) > 0 and 'number' in store['contact']['phoneNumbers'][0]:
                phone = handle_missing(store['contact']['phoneNumbers'][0]['number'])
            location_type = handle_missing(store['name'].split(' ')[-1])
            hours_of_operation = '<MISSING>'
            if 'openingHours' in store:
                hours_of_operation = parse_hours(store['openingHours'])
            locations.append([locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
        if len(stores) <= MAX_RESULTS:
            print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + MAX_RESULTS + " results")
        coord = search.next_coord()
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
