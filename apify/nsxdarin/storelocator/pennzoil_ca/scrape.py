import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locations = []
    for x in range(41, 64):
        for y in range(-52, -141, -1):
            print('%s-%s...' % (str(x), str(y)))
            website = 'pennzoil.ca'
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
                state = item['state']
                zc = item['postcode']
                country = 'CA'
                phone = item['telephone']
                if phone == '':
                    phone = '<MISSING>'
                hours = '<MISSING>'
                typ = '<MISSING>'
                canada = ['NL','NS','PE','QC','ON','BC','AB','MB','SK','YT','NU']
                info = add + ';' + city + ';' + state
                if store not in locations and state in canada:
                    locations.append(store)
                    if 'PENNZOIL' in name.upper():
                        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
