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
    locs = []
    url = 'https://www.forever21.com/eu/shop/Info/GetFindStoreList'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['F21StoreList']:
        if item['CountryName'] == 'U.S.A':
            add = item['Address'] + ' ' + item['Address2']
            city = item['City']
            country = 'US'
            website = 'forever21.com'
            typ = '<MISSING>'
            lat = item['Latitude']
            lng = item['Longitude']
            state = item['State']
            loc = '<MISSING>'
            name = item['Location']
            zc = item['ZIP']
            phone = item['Phone']
            store = item['StoreID']
            hours = 'Mon: ' + item['Monday']
            hours = hours + '; Tue: ' + item['Tuesday']
            hours = hours + '; Wed: ' + item['Wednesday']
            hours = hours + '; Thu: ' + item['Thursday']
            hours = hours + '; Fri: ' + item['Friday']
            hours = hours + '; Sat: ' + item['Saturday']
            hours = hours + '; Sun: ' + item['Sunday']
            if hours == '':
                hours = '<MISSING>'
            if zc == '':
                zc = '<MISSING>'
            if 'AM' not in hours:
                hours = '<MISSING>'
            if '0.000000' in lat:
                lat = '<MISSING>'
                lng = '<MISSING>'
            hours = hours.replace('\t','').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
