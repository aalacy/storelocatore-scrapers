import csv
import urllib2
from sgrequests import SgRequests
import json
import sgzip

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for code in sgzip.for_radius(200):
        print('Pulling Zip Code %s...' % code)
        url = 'https://www.mapquestapi.com/search/v2/radius?key=Gmjtd|lu6tnu0bn9,85=o5-lw220&origin=' + code + '+US&radius=200&hostedData=mqap.34107_bcf_stores&_=1569251207933'
        r = session.get(url, headers=headers)
        if 'searchResults' in r.content:
            array = json.loads(r.content)
            for item in array['searchResults']:
                store = item['name']
                name = 'Burlington Store #' + store
                phone = item['fields']['phone']
                add = item['fields']['address'].encode('utf-8')
                lat = item['fields']['mqap_geography']['latLng']['lat']
                lng = item['fields']['mqap_geography']['latLng']['lng']
                website = 'burlington.com'
                city = item['fields']['city'].encode('utf-8')
                state = item['fields']['state'].encode('utf-8')
                zc = item['fields']['postal'].encode('utf-8')
                country = 'US'
                typ = 'Store'
                hours = item['fields']['hours1'] + ' ' + item['fields']['hours2'] + ' ' + item['fields']['hours3']
                hours = hours.strip().encode('utf-8')
                if store not in ids:
                    ids.append(store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
