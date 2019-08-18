import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.whitecastle.com/sitemap.xml'
    r = session.get(url, verify=False, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.whitecastle.com/locations/' in line:
            locs.append(line.split('locations/')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        lurl = 'https://www.whitecastle.com/wcapi/location-by-store-number?storeNumber=' + loc
        website = 'whitecastle.com'
        name = 'White Castle #' + loc
        store = loc
        hours = ''
        r2 = session.get(lurl, headers=headers)
        array = json.loads(r2.content)
        add = array['address']
        city = array['city']
        state = array['state']
        zc = array['zip']
        phone = array['telephone']
        country = 'US'
        if array['open24x7']:
            hours = 'Open 24 Hours'
        else:
            for hr in array['days']:
                day = hr['day']
                if not hr['open24Hours']:
                    time = hr['hours']
                else:
                    time = 'Open 24 Hours'
                if hours == '':
                    hours = day + ': ' + time
                else:
                    hours = hours + '; ' + day + ': ' + time
        typ = 'Restaurant'
        lat = array['lat']
        lng = array['lng']
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
