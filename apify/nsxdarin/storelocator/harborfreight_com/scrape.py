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
    states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA',
              'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI',
              'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV',
              'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UM',
              'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY']
    
    url = 'https://shop.harborfreight.com/storelocator/location/map'
    for state in states:
        url2 = 'https://shop.harborfreight.com/storelocator/location/state?lat=&lng=&state=' + state + '&radius=3000&justState=true&stateValue=' + state
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
                        hours = ''
                        try:
                            hours = 'M-F: ' + item.split('store_hours_mf="')[1].split('"')[0]
                            hours = hours + '; Sat: ' + item.split('store_hours_sat="')[1].split('"')[0]
                            hours = hours + '; Sun: ' + item.split('store_hours_sun="')[1].split('"')[0]
                        except:
                            pass
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
