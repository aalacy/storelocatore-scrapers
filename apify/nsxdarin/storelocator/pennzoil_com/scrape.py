import csv
import urllib2
from sgrequests import SgRequests
import sgzip
import json

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

MAX_RESULTS = 50
MAX_DISTANCE = 5

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = set()
    locations = []
    coord = search.next_coord()
    while coord:
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        website = 'pennzoil.com'
        url = 'https://locator.pennzoil.com/api/v1/pennzoil/oil_change_locations/nearest_to?limit=50&lat=' + str(x) + '&lng=' + str(y) + '&format=json'
        r = session.get(url, headers=headers)
        result_coords = []
        purl = '<MISSING>'
        array = []
        for item in json.loads(r.content):
            store = item['id'].encode('utf-8')
            name = item['name'].encode('utf-8')
            lat = item['lat']
            lng = item['lng']
            result_coords.append((lat, lng))
            add = item['address1'].encode('utf-8')
            city = item['city'].encode('utf-8')
            state = item['state'].encode('utf-8')
            zc = item['postcode']
            country = 'US'
            phone = item['telephone']
            if phone == '':
                phone = '<MISSING>'
            hours = '<MISSING>'
            typ = '<MISSING>'
            info = add + ';' + city + ';' + state
            ids.add(info)
            array.append(info)
            canada = ['NL','NS','PE','QC','ON','BC','AB','MB','SK','YT','NU','NT','NB']
            if store not in locations and state not in canada:
                locations.append(store)
                if 'PENNZOIL' in name.upper():
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if len(array) <= MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
##        elif len(array) == MAX_RESULTS:
##            print("max count update")
##            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
