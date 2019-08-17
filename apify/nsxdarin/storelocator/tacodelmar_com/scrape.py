import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for x in range(19, 25, 3):
        for y in range(-150, -160, -3):
            print('Pulling Lat/Long %s-%s...' % (str(x), str(y)))
            url = 'https://tacodelmar.com/wp-admin/admin-ajax.php'
            payload = {'lat': str(x),
                       'lng': str(y),
                       'options[default_page_status]': 'draft',
                       'action': 'csl_ajax_search',
                       'radius': '5000'
                       }
            r = session.post(url, headers=headers, data=payload)
            array = json.loads(r.content)
            for item in array['response']:
                website = 'tacodelmar.com'
                name = item['name']
                add = item['address']
                add = add + ' ' + item['address2']
                city = item['city']
                state = item['state']
                zc = item['zip']
                phone = item['phone']
                if phone == '':
                    phone = '<MISSING>'
                hours = item['hours'].replace('&lt;br&gt;','; ').replace('\\r','').replace('\\n','').replace('\r','').replace('\n','')
                country = item['country']
                typ = 'Restaurant'
                store = item['id']
                lat = item['lat']
                lng = item['lng']
                if country == 'USA':
                    country = 'US'
                else:
                    country = 'CA'
                if country == 'CA' and ' ' not in zc:
                    zc = zc[:3] + ' ' + zc[-3:]
                if store not in ids:
                    ids.append(store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    for x in range(24, 57, 3):
        for y in range(-60, -125, -3):
            print('Pulling Lat/Long %s-%s...' % (str(x), str(y)))
            url = 'https://tacodelmar.com/wp-admin/admin-ajax.php'
            payload = {'lat': str(x),
                       'lng': str(y),
                       'options[default_page_status]': 'draft',
                       'action': 'csl_ajax_search',
                       'radius': '5000'
                       }
            r = session.post(url, headers=headers, data=payload)
            array = json.loads(r.content)
            for item in array['response']:
                website = 'tacodelmar.com'
                name = item['name']
                add = item['address']
                add = add + ' ' + item['address2']
                city = item['city']
                state = item['state']
                zc = item['zip']
                phone = item['phone']
                if phone == '':
                    phone = '<MISSING>'
                hours = item['hours'].replace('&lt;br&gt;','; ').replace('\\r','').replace('\\n','').replace('\r','').replace('\n','')
                country = item['country']
                typ = 'Restaurant'
                store = item['id']
                lat = item['lat']
                lng = item['lng']
                if country == 'USA':
                    country = 'US'
                else:
                    country = 'CA'
                if country == 'CA' and ' ' not in zc:
                    zc = zc[:3] + ' ' + zc[-3:]
                if store not in ids:
                    ids.append(store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
