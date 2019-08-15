import csv
import urllib2
import requests

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
            for line in r.iter_lines():
                if '{"name":"' in line:
                    items = line.split('{"name":"')
                    for item in items:
                        if '"email":"' in item:
                            website = 'tacodelmar.com'
                            name = item.split('"')[0].replace('&amp;','&')
                            add = item.split('"address":"')[1].split('"')[0]
                            if '"address2":""' not in item:
                                add = add + ' ' + item.split('"address2":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            state = item.split('"state":"')[1].split('"')[0]
                            zc = item.split('"zip":"')[1].split('"')[0]
                            phone = item.split('"phone":"')[1].split('"')[0]
                            hours = item.split('"hours":"')[1].split('"')[0].replace('&lt;br&gt;','; ')
                            country = item.split('"country":"')[1].split('"')[0]
                            typ = 'Restaurant'
                            store = item.split('"id":"')[1].split('"')[0].strip()
                            lat = item.split('"lat":"')[1].split('"')[0]
                            lng = item.split('"lng":"')[1].split('"')[0]
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
