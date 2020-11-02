import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    locs = []
    coords = []
    url = 'https://www.texadelphia.com/wp-content/themes/texsite/json/locations-v1.json'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'texadelphia.com'
    typ = '<MISSING>'
    store = '<MISSING>'
    for line in r.iter_lines(decode_unicode=True):
        if '"name":' in line:
            name = line.split('"name":')[1].split('"')[1]
        if '"address": "' in line:
            add = line.split('"address": "')[1].split('"')[0]
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
        if '"state": "' in line:
            state = line.split('"state": "')[1].split('"')[0]
        if '"zip": "' in line:
            zc = line.split('"zip": "')[1].split('"')[0]
            country = 'US'
        if '"phone": "' in line:
            phone = line.split('"phone": "')[1].split('"')[0]
        if '"hours1": "' in line:
            hours = line.split('"hours1": "')[1].split('"')[0]
        if '"hours2": "' in line and '""' not in line:
            hours = hours + '; ' + line.split('"hours2": "')[1].split('"')[0]
        if '"hours3": "' in line and '""' not in line:
            hours = hours + '; ' + line.split('"hours3": "')[1].split('"')[0]
        if '"lat":' in line:
            lat = line.split('"lat":')[1].split(',')[0].strip()
        if '"lng":' in line:
            lng = line.split('"lng":')[1].split(',')[0].strip()
            loc = '<MISSING>'
            if 'Coming' not in hours:
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
