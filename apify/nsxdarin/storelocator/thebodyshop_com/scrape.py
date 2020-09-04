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
    url = 'https://www.thebodyshop.com/en-ca/store-finder/search?country=CA'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['stores']:
        typ = item['storeType']
        website = 'thebodyshop.com'
        store = item['uniqueId']
        if 'number' in item and item['number']:
            phone = item['number']
        else:
            phone = '<MISSING>'
        add = item['address']
        if item['address2']:
            add = add + ' ' + item['address2']
        city = item['zip']
        state = item['city'].strip().split(' ')[0]
        zc = item['zip']
        if item['state']:
            state = item['state']
        city = item['city']
        country = item['country']['isocode']
        lurl = '<MISSING>'
        lat = item['latlong'][0]
        lng = item['latlong'][1]
        name = item['name']
        try:
            hours = 'Mon: ' + item['open']['mo'][0] + '-' + item['open']['mo'][1]
        except:
            hours = 'Mon: Closed'
        try:
            hours = hours + '; Tue: ' + item['open']['tu'][0] + '-' + item['open']['tu'][1]
        except:
            hours = hours + '; Tue: Closed'
        try:
            hours = hours + '; Wed: ' + item['open']['we'][0] + '-' + item['open']['we'][1]
        except:
            hours = hours + '; Wed: Closed'
        try:
            hours = hours + '; Thu: ' + item['open']['th'][0] + '-' + item['open']['th'][1]
        except:
            hours = hours + '; Thu: Closed'
        try:
            hours = hours + '; Fri: ' + item['open']['fr'][0] + '-' + item['open']['fr'][1]
        except:
            hours = hours + '; Fri: Closed'
        try:
            hours = hours + '; Sat: ' + item['open']['sa'][0] + '-' + item['open']['sa'][1]
        except:
            hours = hours + '; Sat: Closed'
        try:
            hours = hours + '; Sun: ' + item['open']['su'][0] + '-' + item['open']['su'][1]
        except:
            hours = hours + '; Sun: Closed'
        state = state.replace(',','').strip()
        if hours == 'Mon: Closed;Tue: Closed;Wed: Closed;Thu: Closed;Fri: Closed;Sat: Closed;Sun: Closed':
            hours = '<MISSING>'
        if city == 'Barrie' or city == 'Toronto':
            state = 'Ontario'
        if city == 'Saskatoon':
            state = 'Saskatchewan'
        if hours == '':
            hours = '<MISSING>'
        if 'Mon: Closed;' in hours or 'Mon:Closed' in hours:
            hours = '<MISSING>'
        if '/' in phone:
            phone = phone.split('/')[0].strip()
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    url = 'https://www.thebodyshop.com/en-us/store-finder/search?country=US'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['stores']:
        typ = item['storeType']
        website = 'thebodyshop.com'
        store = item['uniqueId']
        if 'number' in item and item['number']:
            phone = item['number']
        else:
            phone = '<MISSING>'
        add = item['address']
        if item['address2']:
            add = add + ' ' + item['address2']
        city = item['zip']
        state = item['city'].strip().split(' ')[0]
        try:
            zc = item['city'].strip().split(' ')[1]
            if 'a' in zc.lower() or 'e' in zc.lower() or 'i' in zc.lower() or 'o' in zc.lower() or 'u' in zc.lower():
                zc = item['zip']
                city = item['city']
                state = item['state']
            else:
                zc = zc
        except:
            zc = item['zip']
            city = item['city']
            state = item['state']
        if city == 'Fort Lauderdale':
            state = 'FL'
        country = item['country']['isocode']
        lurl = '<MISSING>'
        lat = item['latlong'][0]
        lng = item['latlong'][1]
        name = item['name']
        try:
            hours = 'Mon: ' + item['open']['mo'][0] + '-' + item['open']['mo'][1]
        except:
            hours = 'Mon: Closed'
        try:
            hours = hours + '; Tue: ' + item['open']['tu'][0] + '-' + item['open']['tu'][1]
        except:
            hours = hours + '; Tue: Closed'
        try:
            hours = hours + '; Wed: ' + item['open']['we'][0] + '-' + item['open']['we'][1]
        except:
            hours = hours + '; Wed: Closed'
        try:
            hours = hours + '; Thu: ' + item['open']['th'][0] + '-' + item['open']['th'][1]
        except:
            hours = hours + '; Thu: Closed'
        try:
            hours = hours + '; Fri: ' + item['open']['fr'][0] + '-' + item['open']['fr'][1]
        except:
            hours = hours + '; Fri: Closed'
        try:
            hours = hours + '; Sat: ' + item['open']['sa'][0] + '-' + item['open']['sa'][1]
        except:
            hours = hours + '; Sat: Closed'
        try:
            hours = hours + '; Sun: ' + item['open']['su'][0] + '-' + item['open']['su'][1]
        except:
            hours = hours + '; Sun: Closed'
        try:
            state = state.replace(',','').strip()
        except:
            state = '<MISSING>'
        if hours == 'Mon: Closed;Tue: Closed;Wed: Closed;Thu: Closed;Fri: Closed;Sat: Closed;Sun: Closed':
            hours = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if 'Mon: Closed;' in hours or 'Mon:Closed' in hours:
            hours = '<MISSING>'
        if '/' in phone:
            phone = phone.split('/')[0].strip()
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
