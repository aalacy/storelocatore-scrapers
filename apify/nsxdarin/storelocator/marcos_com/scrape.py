import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('datamarcos.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.marcos.com/api/stores/getAllStore?listStores=true'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['results']:
        name = item['name']
        country = 'US'
        store = name.split(' ')[0]
        try:
            purl = item['baseUrl']
        except:
            purl = '<MISSING>'
        add = item['address']
        try:
            phone = item['telephone']
        except:
            phone = '<MISSING>'
        try:
            zc = item['zip']
        except:
            zc = '<MISSING>'
        try:
            state = item['state']
        except:
            state = '<MISSING>'
        try:
            city = item['city']
        except:
            city = '<MISSING>'
        lat = item['lat']
        lng = item['lng']
        if lat == '0':
            lat = '<MISSING>'
            lng = '<MISSING>'
        hours = '<MISSING>'
        website = 'marcos.com'
        typ = 'Restaurant'
        if '#' in name:
            store = name.split('#')[1].strip()
        if '999-' not in phone and state != 'BH' and state != '<MISSING>':
            if purl == '<MISSING>' and store == '8533':
                pass
            else:
                if "u'status', u'value': 2" not in str(item):
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
