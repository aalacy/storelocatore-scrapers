import csv
from sgzip import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('t-mobile_com')

search = DynamicGeoSearch(country_codes=[SearchableCountries.USA], max_radius_miles=50)
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'authority': 'www.t-mobile.com',
           'accept': 'application/json, text/plain, */*',
           'clientapplicationid': 'OCNATIVEAPP',
           'loginin': 'mytest016@outlook.com',
           'locale': 'en_US'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def parse_hours(store):
    if 'standardHours' not in store or not store['standardHours']:
        return '<MISSING>'
    hours = []
    days = store['standardHours'] 
    for day in days:
        if "opens" in day:
            hours.append('{}: {}-{}'.format(day['day'], day['opens'], day['closes']))
    return ', '.join(hours)

def compute_location_type(store):
    statusDefinition = store['storeDefinition']
    deviceRepair = store['deviceRepair']
    hasSprintStack = store['hasSprintStack']
    hasTmobileStack = store['hasTmobileStack']
    tags = store['storeTag']
    if statusDefinition == None and hasSprintStack is False and hasTmobileStack is False:
        return 'T-Mobile Authorized Dealer'
    elif 'signature' in tags:
        return 'T-Mobile Signature Store'
    elif hasSprintStack is True and hasTmobileStack is False:
        return 'Sprint Store'
    elif deviceRepair is False and hasTmobileStack is True and 'FPR' in statusDefinition:
        return 'T-Mobile Store'
    elif deviceRepair is False and 'TPR' in statusDefinition:
        return 'T-Mobile Authorized Retailer'
    elif deviceRepair is True and hasSprintStack is True and hasTmobileStack is True and 'FPR' in statusDefinition:
        return 'T-Mobile Store (Sprint Repair Center)'
    else:
        print("************************************")
        print('type: ' + store['type'])
        print('statusDefinition: ' + store['storeDefinition'])
        print('streetAddress: ' + store['location']['address']['streetAddress'])
        print('zip: ' + store['location']['address']['postalCode'])
        print('storeDistance: ' + str(store['storeDistance']))
        print('deviceRepair: ' + str(store['deviceRepair']))
        print('hasSprintStack: ' + str(store['hasSprintStack']))
        print('hasTmobileStack: ' + str(store['hasTmobileStack']))

def handle_missing(x):
    if not x or not x.strip():
        return '<MISSING>'
    return x

def fetch_data():
    keys = set()
    coord = search.next()
    while coord:
        llat, llng = coord
        url = 'https://onmyj41p3c.execute-api.us-west-2.amazonaws.com/prod/v2.1/getStoresByCoordinates?latitude=' + str(llat) + '&longitude=' + str(llng) + '&count=50&radius=100&ignoreLoadin{%22id%22:%22gBar=false'
        stores = session.get(url, headers=headers).json()
        result_coords = []
        website = 't-mobile.com'
        if 'code' not in stores:
            for store in stores:
                if 'name' in store:
                    name = store['name'] 
                else:
                    name = '<MISSING>'
                store_id = store['id'] 
                location_type = compute_location_type(store) 
                if 'url' in store:
                    loc = store['url'] 
                else:
                    loc = '<MISSING>'
                phone = handle_missing(store['telephone'])
                location = store['location']
                address = location['address']
                add = handle_missing(address['streetAddress'])
                city = handle_missing(address["addressLocality"])
                state = handle_missing(address["addressRegion"])
                zc = handle_missing(address["postalCode"])
                country = 'US'
                lat = location["latitude"]
                lng = location["longitude"]
                result_coords.append((lat, lng))
                hours = parse_hours(store)
                if store_id not in keys:
                    keys.add(store_id)
                    yield [website, loc, name, add, city, state, zc, country, store_id, phone, location_type, lat, lng, hours]
        search.update_with(result_coords)
        coord = search.next()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
