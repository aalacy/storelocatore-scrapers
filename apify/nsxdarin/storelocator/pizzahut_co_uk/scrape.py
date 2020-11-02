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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://api.pizzahut.io/v1/huts/?sector=uk-1,uk-2&featureRole=none'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item['id']
        name = item['name']
        try:
            add = item['address']['lines'][0] + ' ' + item['address']['lines'][1]
            add = add.strip()
            city = item['address']['lines'][2]
        except:
            add = item['address']['lines'][0]
            add = add.strip()
            city = item['address']['lines'][1]
        zc = item['address']['postcode']
        country = 'GB'
        loc = url
        state = '<MISSING>'
        website = 'pizzahut.co.uk'
        typ = item['type']
        lat = item['latitude']
        lng = item['longitude']
        phone = item['phone']
        hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
