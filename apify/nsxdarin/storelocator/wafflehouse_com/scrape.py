import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://locations.wafflehouse.com/api/587d236eeb89fb17504336db/locations-details?locale=en_US&ids='
    r = session.get(url, headers=headers, stream=True)
    for item in json.loads(r.content)['features']:
        name = item['properties']['name']
        store = item['properties']['branch']
        add = item['properties']['addressLine1']
        add2 = item['properties']['addressLine2']
        add = add + ' ' + add2
        add = add.strip()
        city = item['properties']['city']
        state = item['properties']['province']
        zc = item['properties']['postalCode']
        phone = item['properties']['phoneNumber']
        lat = item['geometry']['coordinates'][0]
        lng = item['geometry']['coordinates'][1]
        country = 'US'
        website = 'wafflehouse.com'
        typ = 'Restaurant'
        hours = '24/7'
        loc = 'https://locations.wafflehouse.com/' + item['properties']['slug']
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
