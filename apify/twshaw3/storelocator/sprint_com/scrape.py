import csv
from sgrequests import SgRequests
import sgzip
import os

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "operating_info"])
        # Body
        for row in data:
            writer.writerow(row)

HEADERS = {
    'Host': 'storelocator.sprint.com',
    'Referer': 'https://storelocator.sprint.com/locator/\?INTNAV\=TopNav:LocateStore',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

URL_TEMPLATE = "https://storelocator.sprint.com/locator/GetData.ashx?loc={}&r=500&sar=1"

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()

MAX_RESULTS = 99
MAX_DISTANCE = 500.0

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def fetch_data():
    keys = set()
    locations = []
    zipcode = search.next_zip()
    while zipcode:
        print(zipcode)
        print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        url = URL_TEMPLATE.format(zipcode)
        stores = session.get(url, headers=HEADERS).json()['Hits']
        print(len(stores))
        result_coords = []
        for store in stores:
            data = store['Retailer']
            store_number = handle_missing(str(data['LocationId']))
            latitude = handle_missing(data['LatLon']['Latitude'])
            longitude = handle_missing(data['LatLon']['Longitude'])
            result_coords.append((latitude, longitude))
            street_address = handle_missing(data['PostalAddress']['Address1'])
            city = handle_missing(data['PostalAddress']['City'])
            state = handle_missing(data['PostalAddress']['State'])
            zip_code = handle_missing(data['PostalAddress']['Zip'])
            key = "{}|{}|{}|{}".format(street_address, city, state, zip_code)
            if key not in keys:
                keys.add(key)
                locator_domain = 'sprint.com'
                country_code = 'US'
                location_name = handle_missing(data['Name'])
                location_type = handle_missing(data['Type'])
                page_url = handle_missing(data['Url'])
                phone = handle_missing(data['PhoneNumber'])
                hours_of_operation = str(handle_missing(data['SalesHours']))
                operating_info = '<MISSING>'
                if hours_of_operation.lower().count('closed') == 7:
                    operating_info = 'Temporarily Closed'
                record = [locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, operating_info]
                locations.append(record)
        if len(stores) < MAX_RESULTS:
            print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(stores) == MAX_RESULTS:
            print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + MAX_RESULTS + " results")
        zipcode = search.next_zip()
    return locations

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
