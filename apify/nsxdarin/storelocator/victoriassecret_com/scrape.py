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
    urls = ['https://api.victoriassecret.com/stores/v1/search?countryCode=CA','https://api.victoriassecret.com/stores/v1/search?countryCode=US']
    for url in urls:
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        for item in array:
            store = item['storeId']
            purl = 'https://www.victoriassecret.com/store-locator#store/' + store
            name = item['name']
            add = item['address']['streetAddress1']
            city = item['address']['city']
            state = item['address']['region']
            zc = item['address']['postalCode']
            phone = item['address']['phone']
            lat = item['latitudeDegrees']
            lng = item['longitudeDegrees']
            typ = str(item['productLines']).replace('[','').replace(']','').replace("u'",'').replace("'",'')
            country = item['address']['countryCode']
            website = 'victoriassecret.com'
            hours = ''
            lurl = 'https://api.victoriassecret.com/stores/v1/store/' + store
            r2 = session.get(lurl, headers=headers)
            week = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
            for day in json.loads(r2.content)['hours']:
                if hours == '':
                    hours = week[day['day'] - 1] + ': ' + day['open'] + '-' + day['close']
                else:
                    hours = hours + '; ' + week[day['day'] - 1] + ': ' + day['open'] + '-' + day['close']
            if typ == '':
                typ = '<MISSING>'
            if lat == '':
                lat = '<MISSING>'
                lng = '<MISSING>'
            if hours == '':
                hours = '<MISSING>'
            if '000' in phone:
                phone = '<MISSING>'
            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
