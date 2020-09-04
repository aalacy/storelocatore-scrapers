import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'Accept': 'application/json, text/plain, */*',
           'Connection': 'keep-alive',
           'Content-Type': 'application/json;charset=utf-8',
           'Referer': 'https://www.loblaws.ca/store-locator/details/',
           'Sec-Fetch-Dest': 'empty',
           'Sec-Fetch-Mode': 'cors',
           'Sec-Fetch-Site': 'same-origin',
           'Site-Banner': 'loblaw',
           'Host': 'www.loblaws.ca'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    for x in range(1000, 2000):
        print(x)
        url = 'https://www.loblaws.ca/api/pickup-locations/' + str(x)
        r = session.get(url, headers=headers)
        if 'Could not find' not in r.content and 'storeDetails' in r.content:
            array = json.loads(r.content)
            loc = 'https://www.loblaws.ca/store-locator/details/' + str(x)
            store = str(x)
            try:
                phone = array['storeDetails']['phoneNumber']
            except:
                phone = '<MISSING>'
            name = array['name']
            website = 'loblaws.com'
            typ = array['storeBannerName'] + '-' + array['locationType']
            lat = array['geoPoint']['latitude']
            lng = array['geoPoint']['longitude']
            country = 'CA'
            state = array['address']['region']
            city = array['address']['town']
            zc = array['address']['postalCode']
            try:
                add = array['address']['line1'] + ' ' + array['address']['line2']
            except:
                add = array['address']['line1']
            add = add.strip()
            hours = ''
            for item in array['storeDetails']['storeHours']:
                hrs = item['day'] + ': ' + item['hours']
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if hours == '':
                hours = '<MISSING>'
            if phone == '':
                phone = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
