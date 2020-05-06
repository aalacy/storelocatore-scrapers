import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'application/json',
           'x-requested-with': 'XMLHttpRequest'
           }

headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.plannedparenthood.org/abortion-access/_health_centres'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"pk": "' in line:
            items = line.split('"pk": "')
            for item in items:
                if '"ppfa_facility":' in item:
                    hours = ''
                    loc = 'https://www.plannedparenthood.org' + item.split('"absolute_url": "')[1].split('"')[0]
                    store = item.split('"')[0]
                    print(store)
                    name = item.split('"name": "')[1].split('"')[0]
                    typ = '<MISSING>'
                    website = 'plannedparenthood.org'
                    lng = item.split('"lng": ')[1].split(',')[0]
                    lat = item.split('"lat": ')[1].split('}')[0]
                    add = item.split('"address": "')[1].split('"')[0]
                    city = item.split('"city": "')[1].split('"')[0]
                    state = item.split('"state": "')[1].split('"')[0]
                    phone = item.split('"phone": ')[1].split('"display": "')[1].split('"')[0]
                    zc = item.split('"zipcode": "')[1].split('"')[0]
                    country = 'US'
                    print('Pulling Location %s...' % loc)
                    r2 = session.get(loc, headers=headers2)
                    for line2 in r2.iter_lines():
                        if '"openingHours": ["' in line2:
                            hours = line2.split('"openingHours": ["')[1].split(']')[0].replace('", "','; ').replace('"','')
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
