import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import time
import sgzip 
import os

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

MAX_RESULTS = 15
MAX_DISTANCE = 100.0

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = set()
    locations = []
    coord = search.next_coord()
    while coord:
        print(("remaining zipcodes: " + str(search.zipcodes_remaining())))
        x = coord[0]
        y = coord[1]
        print(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        url = 'https://www.firstwatch.com/api/get_locations.php?latitude=' + str(x) + '&longitude=' + str(y)
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        array = json.loads(r.content)
        result_coords = []
        for item in array:
            lat = item['latitude']
            lng = item['longitude']
            result_coords.append((lat, lng))
            store = item['corporate_id']
            if store in ids: continue
            website = 'firstwatch.com'
            hours = '<MISSING>'
            name = item['name']
            add = item['address'] + ' ' + item['address_extended']
            add = add.strip()
            phone = item['phone']
            slug = item['slug']
            surl = 'https://www.firstwatch.com/locations/' + slug
            r2 = session.get(surl, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            for line2 in r2.iter_lines(decode_unicode=True):
                if '<address>Open' in line2:
                    hours = line2.split('<address>')[1].split('<')[0]
            typ = 'Restaurant'
            city = item['city']
            state = item['state']
            zc = item['zip']
            country = 'US'
            store = item['corporate_id']
            ids.add(store)
            print(('Pulling Store ID #%s...' % store))
            locations.append([website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours])
        if len(array) < MAX_RESULTS:
            print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(array) == MAX_RESULTS:
            print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + MAX_RESULTS + " results")
        coord = search.next_coord()
    for loc in locations:
        yield loc

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
