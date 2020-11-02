import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import sgzip

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

MAX_RESULTS = 1000
MAX_DISTANCE = 5.0

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    coord = search.next_zip()
    while coord:
        website = 'littlecaesars.com'
        url = 'https://api.cloud.littlecaesars.com/bff/api/stores?zip=' + coord
        r = session.get(url, headers=headers, verify=False)
        result_coords = []
        array = []
        for item in json.loads(r.content)['stores']:
            name = "Little Caesar's"
            city = item['address']['city']
            state = item['address']['state']
            country = 'US'
            add = item['address']['street'] + ' ' + item['address']['street2']
            add = add.strip()
            zc = item['address']['zip']
            lat = item['latitude']
            lng = item['longitude']
            phone = item['phone']
            store = item['storeId']
            typ = item['storeType']
            purl = 'https://order.littlecaesars.com/en-us/stores/' + str(store)
            try:
                hours = item['storeOpenTime'] + '-' + item['storeCloseTime']
            except:
                hours = '<MISSING>'
            array.append(store)
            if store not in ids:
                ids.append(store)
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if len(array) <= MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
