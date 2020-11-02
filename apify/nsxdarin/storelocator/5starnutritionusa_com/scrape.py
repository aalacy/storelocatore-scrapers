import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    url = 'https://stockist.co/api/v1/u3959/locations/all.js?callback=_stockistAllStoresCallback'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = '5starnutritionusa.com'
    for line in r.iter_lines(decode_unicode=True):
        if '"id":' in line:
            items = line.split('"id":')
            for item in items:
                if '"name":"' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    store = item.split(',')[0]
                    loc = '<MISSING>'
                    typ = '<MISSING>'
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    add = item.split('"address_line_1":"')[1].split('"')[0]
                    if '"address_line_2":"' in item:
                        add = add + ' ' + item.split('"address_line_2":"')[1].split('"')[0]
                    try:
                        zc = item.split('"postal_code":"')[1].split('"')[0]
                    except:
                        zc = '<MISSING>'
                    country = 'US'
                    try:
                        state = item.split('"state":"')[1].split('"')[0]
                    except:
                        state = '<MISSING>'
                    if zc == '71292':
                        state = 'LA'
                    phone = item.split('"phone":"')[1].split('"')[0]
                    try:
                        hours = item.split('"description":"')[1].split('"')[0].replace('day\\t','day: ').replace('\\u2013','-').replace('\\n','; ')
                    except:
                        hours = '<MISSING>'
                    if '1800 McFarland Blvd' in add:
                        zc = '35404'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
