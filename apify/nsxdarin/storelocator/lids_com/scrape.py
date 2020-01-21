import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.lids.com/api/stores?lat=46.5926188&long=-120.5363432&num=5000&shipToStore=false'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item['storeId']
        name = item['name'].encode('utf-8')
        add = item['address1'].encode('utf-8')
        try:
            add = add + ' ' + item['address2'].encode('utf-8')
            add = add.strip()
        except:
            pass
        city = item['city'].encode('utf-8')
        state = item['state']
        country = item['country']
        phone = item['phone']
        zc = item['zip']
        lat = item['latitude']
        lng = item['longitude']
        typ = item['storeBrand'].encode('utf-8')
        hours = 'Mon-Fri: ' + item['monFriOpen'] + '-' + item['monFriClose']
        hours = hours + '; Sat: ' + item['satOpen'] + '-' + item['satClose']
        hours = hours + '; Sun: ' + item['sunOpen'] + '-' + item['sunClose']
        website = 'lids.com'
        loc = 'https://lids.com' + item['untaggedURL']
        if country == 'US':
            if phone == '':
                phone = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
