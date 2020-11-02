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
    url = 'https://www.harley-davidson.com/dealerservices/services/rest/dealers/proximitySearch.json?_type=json&size=2500&latlng=45%2C-95&miles=10000&locale=en_US'
    r = session.get(url, headers=headers)
    items = r.text.split('"authCode":"')
    for item in items:
        if '"commerceInfo":' in item:
            website = 'harley-davidson.com'
            typ = item.split('"')[0]
            add = item.split('"address1":"')[1].split('"')[0]
            try:
                add = add + ' ' + item.split('"address2":"')[1].split('"')[0]
            except:
                pass
            city = item.split('"city":"')[1].split('"')[0]
            try:
                state = item.split('"state":"')[1].split('"')[0]
            except:
                state = '<MISSING>'
            country = item.split('"country":"')[1].split('"')[0]
            country = country[:2]
            if country == 'US' or country == 'CA':
                phone = item.split('"phoneNumber":"')[1].split('"')[0]
                lat = item.split('"latitude":"')[1].split('"')[0]
                lng = item.split('"longitude":"')[1].split('"')[0]
                zc = item.split('"postalCode":"')[1].split('"')[0]
                name = item.split('"name":"')[1].split('"')[0]
                store = item.split('"id":"')[1].split('"')[0]
                try:
                    hours = item.split('"dealerHours":"')[1].split('<br/>"')[0].replace('<br/>','; ')
                except:
                    hours = '<MISSING>'
                loc = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
