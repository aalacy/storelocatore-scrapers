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
    url = 'https://ww8.ikea.com/ext/iplugins/v2/en_US/data/localstorefinder/data.json'
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array:
        store = item['storeId']
        name = 'Ikea #' + str(store)
        add = item['storeAddress']
        city = item['storeCity']
        state = item['storeState']
        zc = item['storeZip']
        phone = '1-888-888-4532'
        website = 'ikea.com'
        typ = 'Store'
        country = 'US'
        hours = 'Sun: ' + item['storeHours'][0]['openHours'] + ':' + item['storeHours'][0]['openMinutes'] + '-' + item['storeHours'][0]['closeHours'] + ':' + item['storeHours'][0]['closeMinutes']
        hours = hours + '; Mon: ' + item['storeHours'][1]['openHours'] + ':' + item['storeHours'][1]['openMinutes'] + '-' + item['storeHours'][0]['closeHours'] + ':' + item['storeHours'][0]['closeMinutes']
        hours = hours + '; Tue: ' + item['storeHours'][2]['openHours'] + ':' + item['storeHours'][2]['openMinutes'] + '-' + item['storeHours'][0]['closeHours'] + ':' + item['storeHours'][0]['closeMinutes']
        hours = hours + '; Wed: ' + item['storeHours'][3]['openHours'] + ':' + item['storeHours'][3]['openMinutes'] + '-' + item['storeHours'][0]['closeHours'] + ':' + item['storeHours'][0]['closeMinutes']
        hours = hours + '; Thu: ' + item['storeHours'][4]['openHours'] + ':' + item['storeHours'][4]['openMinutes'] + '-' + item['storeHours'][0]['closeHours'] + ':' + item['storeHours'][0]['closeMinutes']
        hours = hours + '; Fri: ' + item['storeHours'][5]['openHours'] + ':' + item['storeHours'][5]['openMinutes'] + '-' + item['storeHours'][0]['closeHours'] + ':' + item['storeHours'][0]['closeMinutes']
        hours = hours + '; Sat: ' + item['storeHours'][6]['openHours'] + ':' + item['storeHours'][6]['openMinutes'] + '-' + item['storeHours'][0]['closeHours'] + ':' + item['storeHours'][0]['closeMinutes']
        lat = item['geoLat']
        lng = item['geoLng']
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
