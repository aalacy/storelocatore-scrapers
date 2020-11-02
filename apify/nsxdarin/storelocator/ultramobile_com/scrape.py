import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

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
    url = 'https://locator-api.ultramobile.com/find?format=jsonp&partner=ultrainfo&command=ultrainfo__GetLocations&bath=rest&version=2&radius=5000&max_entries=5000&latitude=45&longitude=-95&brand=ULTRA&location_type=DEALER'
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array['location_list']:
        store = item['LOCATION_ID']
        name = item['RETAILER_NAME']
        phone = item['RETAILER_PHONE_NUMBER']
        add = item['ADDRESS1'] + ' ' + item['ADDRESS2']
        add = add.strip()
        lat = item['LATITUDE']
        lng = item['LONGITUDE']
        website = 'ultramobile.com'
        city = item['CITY']
        state = item['STATE']
        zc = item['ZIPCODE']
        country = 'US'
        typ = item['LOCATION_TYPE']
        hours = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
