import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
           'x-requested-with': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://lgstoreswv.com/wp-admin/admin-ajax.php'
    payload = {'action': 'locate',
               'address': '',
               'formatted_address': '',
               'locatorNonce': '234f4b7d7c',
               'distance': '500',
               'latitude': '38',
               'longitude': '-82',
               'unit': 'miles',
               'geolocation': 'false',
               'allow_empty_address': 'true'
               }
    r = session.post(url, headers=headers, data=payload)
    array = json.loads(r.content)['results']
    for item in array:
        name = item['title']
        output = item['output'].replace('\r','').replace('\n','').replace('\t','')
        address = output.split('Distance')[1].split('/>',1)[1].split('<a href')[0]
        add = address.split('<')[0]
        city = address.split('>')[1].split(',')[0]
        state = 'WV'
        zc = address.split('>')[1].split('<')[0].rsplit(' ',1)[1]
        phone = address.split('>')[2].split('<')[0]
        website = 'lgstoreswv.com'
        typ = name
        if '|' in typ:
            typ = typ.split('|')[1].strip()
        country = 'US'
        store = item['id']
        hours = '<MISSING>'
        lat = item['latitude']
        lng = item['longitude']
        if phone == '':
            phone = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
