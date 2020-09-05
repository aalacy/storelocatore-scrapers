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
    states = []
    url = 'https://shop.harborfreight.com/storelocator/location/map'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'class="state" href="#' in line:
            states.append(line.split('class="state" href="#')[1].split('"')[0])
    for state in states:
        url2 = 'https://shop.harborfreight.com/storelocator/location/state?lat=&lng=&state=' + state + '&radius=3000&justState=true&stateValue=' + state
        print(('Pulling State %s...' % state))
        r2 = session.get(url2, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'store_num="' in line2:
                items = line2.split('store_num="')
                for item in items:
                    if 'title="' in item:
                        website = 'harborfreight.com'
                        typ = '<MISSING>'
                        store = item.split('"')[0]
                        name = item.split('title="')[1].split('"')[0]
                        add = item.split('address="')[1].split('"')[0]
                        city = item.split('city="')[1].split('"')[0]
                        hours = item.split('notes="Store hours: &lt;div&gt;')[1].split('"')[0].replace('&lt;/div&gt;&lt;div&gt;',';').replace('&lt;/div&gt;','').replace('  ',' ').replace('  ',' ')
                        country = 'US'
                        state = item.split('state="')[1].split('"')[0]
                        zc = item.split('zip="')[1].split('"')[0]
                        lat = item.split('latitude="')[1].split('"')[0]
                        lng = item.split('longitude="')[1].split('"')[0]
                        phone = item.split('phone="')[1].split('"')[0]
                        loc = '<MISSING>'
                        if phone == '':
                            phone = '<MISSING>'
                        if hours == '':
                            hours = '<MISSING>'
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
