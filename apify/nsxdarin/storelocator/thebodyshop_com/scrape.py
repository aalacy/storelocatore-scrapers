import csv
import urllib2
import requests
import json

session = requests.Session()
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
    url = 'https://www.thebodyshop.com/en-us/store-finder/search?country=US'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['stores']:
        typ = item['storeType'].encode('utf-8')
        website = 'thebodyshop.com'
        store = item['uniqueId'].encode('utf-8')
        try:
            phone = item['number'].encode('utf-8')
        except:
            phone = '<MISSING>'
        add = item['address'].encode('utf-8')
        if item['address2']:
            add = add + ' ' + item['address2'].encode('utf-8')
        city = item['zip']
        state = item['city'].strip().encode('utf-8').split(' ')[0]
        zc = item['city'].strip().encode('utf-8').split(' ')[1]
        country = item['country']['isocode'].encode('utf-8')
        lurl = '<MISSING>'
        lat = item['latlong'][0]
        lng = item['latlong'][1]
        name = item['name']
        try:
            hours = 'Mon: ' + item['open']['mo'][0] + '-' + item['open']['mo'][1]
            hours = hours + ';Tue: ' + item['open']['tu'][0] + '-' + item['open']['tu'][1]
            hours = hours + ';Wed: ' + item['open']['we'][0] + '-' + item['open']['we'][1]
            hours = hours + ';Thu: ' + item['open']['th'][0] + '-' + item['open']['th'][1]
            hours = hours + ';Fri: ' + item['open']['fr'][0] + '-' + item['open']['fr'][1]
            hours = hours + ';Sat: ' + item['open']['sa'][0] + '-' + item['open']['sa'][1]
            hours = hours + ';Sun: ' + item['open']['su'][0] + '-' + item['open']['su'][1]
        except:
            hours = '<MISSING>'
        state = state.replace(',','').strip()
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
