import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import time
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
    url = 'https://wae-store-experience-prod.lllapi.com/stores'
    locs = []
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        website = 'lululemon.com'
        typ = '<MISSING>'
        hours = ''
        store = '<MISSING>'
        name = item['name']
        loc = item['websiteUrl']
        city = item['city']
        country = item['country']
        store = item['storeNumber']
        addinfo = item['fullAddress']
        lat = item['latitude']
        lng = item['longitude']
        state = item['state']
        zc = addinfo.rsplit(' ',1)[1]
        add = addinfo.split(',')[0]
        try:
            phone = item['phone']
        except:
            phone = '<MISSING>'
        for day in item['hours']:
            try:
                hrs = day['name'] + ': ' + day['openHour'] + '-' + day['closeHour']
            except:
                hours = day['name'] + ': Closed'
            if hours == '':
                hours = hrs
            else:
                hours = hours + '; ' + hrs
        if country == 'US' or country == 'CA':
            try:
                if len(phone) < 5:
                    phone = '<MISSING>'
            except:
                phone = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
