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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    url = 'https://www.plainscapital.com/Umbraco/Api/LocationsApi/GetLocations'
    r = session.get(url, headers=headers, verify=False)
    array = json.loads(r.content)
    for item in array:
        name = item['name'].encode('utf-8')
        lat = item['lat']
        lng = item['lng']
        typ = item['locationTypes']
        add = item['address'].encode('utf-8') + ' ' + item['address2'].encode('utf-8')
        add = add.strip()
        city = item['city'].encode('utf-8')
        state = item['state'].encode('utf-8')
        country = 'US'
        phone = item['phone'].encode('utf-8')
        zc = item['zip']
        hours = item['bankHours'].encode('utf-8')
        website = 'plainscapital.com'
        store = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
            lng = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
