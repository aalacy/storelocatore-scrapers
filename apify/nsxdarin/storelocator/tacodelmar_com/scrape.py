import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    url = 'https://tacodelmar.com/wp-json/store-locator-plus/v2/locations'
    r = session.get(url, headers=headers2)
    for item in json.loads(r.content):
        ids.append(item['sl_id'])
    for loc in ids:
        print('Pulling Location %s...' % loc)
        url2 = 'https://tacodelmar.com/wp-json/store-locator-plus/v2/locations/' + loc
        r2 = session.get(url2, headers=headers2)
        array = json.loads(r2.content)
        website = 'tacodelmar.com'
        name = array['sl_store']
        add = array['sl_address']
        add = add + ' ' + array['sl_address2']
        city = array['sl_city']
        state = array['sl_state']
        zc = array['sl_zip']
        phone = array['sl_phone']
        hours = array['sl_hours'].replace('</br>','; ').replace('<br>','; ').replace('\r','').replace('\n','').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
        country = array['sl_country']
        typ = 'Restaurant'
        store = array['sl_id']
        lat = array['sl_latitude']
        lng = array['sl_longitude']
        if country == 'USA':
            country = 'US'
        else:
            country = 'CA'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
