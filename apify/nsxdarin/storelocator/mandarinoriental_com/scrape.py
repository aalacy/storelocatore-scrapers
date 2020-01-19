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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.mandarinoriental.com/ajax/getproperties?language=1'
    locs = []
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array['data']['record']:
        hurl = 'https://www.mandarinoriental.com/' + item['homepage'].replace('\\/','/')
        name = item['name'].encode('utf-8')
        website = 'mandarinoriental.com'
        add = '<MISSING>'
        lat = item['latitude']
        lng = item['longitude']
        typ = 'Hotel'
        hours = '<MISSING>'
        city = item['city'].encode('utf-8')
        state = '<MISSING>'
        zc = '<MISSING>'
        country = item['country'].encode('utf-8')
        store = item['properties_id']
        phone = item['phone']
        r2 = session.get(hurl, headers=headers)
        print('Pulling Location %s...' % hurl)
        for line in r2.iter_lines():
            if '"addressRegion">' in line:
                state = line.split('"addressRegion">')[1].split('<')[0]
            if 'itemprop="streetAddress">' in line:
                add = line.split('itemprop="streetAddress">')[1].split('<')[0]
            if '"postalCode">' in line:
                zc = line.split('"postalCode">')[1].split('<')[0]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
