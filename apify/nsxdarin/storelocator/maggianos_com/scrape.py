import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://locations.maggianos.com/locations.geojson'
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array['features']:
        typ = 'Restaurant'
        website = 'maggianos.com'
        country = item['properties']['country']
        lat = item['geometry']['coordinates'][0]
        lng = item['geometry']['coordinates'][1]
        hours = item['properties']['c_hours'].replace('<ul><li><strong>','').replace('</strong>',' ').replace('</li><li>','; ').replace('<strong>','').replace('</ul>','').replace('</li>','')
        hours = hours
        name = item['properties']['business_name']
        store = item['properties']['store_code']
        add = item['properties']['address_line_1'] + ' ' + item['properties']['address_line_2']
        city = item['properties']['city']
        state = item['properties']['state']
        zc = item['properties']['postalCode']
        phone = item['properties']['primary_phone']
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
