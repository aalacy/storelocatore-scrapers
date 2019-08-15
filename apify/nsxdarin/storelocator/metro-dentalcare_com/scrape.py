import csv
import urllib2
import requests

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
    url = 'https://www.metro-dentalcare.com/wp-admin/admin-ajax.php'
    payload = {'action': 'prov_search',
               'data[search_type]': 'all',
               'data[lat]': '45.0',
               'data[lng]': '-93.0',
               'data[sort_field]': 'dentist_last',
               'data[sort_order]': 'ASC'
               }
    
    r = session.post(url, headers=headers, data=payload)
    website = 'metro-dentalcare.com'
    store = ''
    typ = 'Office'
    country = 'US'
    for line in r.iter_lines():
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if '"code":"' in item:
                    phone = item.split('"phone_primary":"')[1].split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0]
                    add2 = item.split('"address2":"')[1].split('"')[0]
                    if add2 != '':
                        add = add + ' ' + add2
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"postal_code":"')[1].split('"')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    hours = 'Mon: ' + item.split('"Monday":["')[1].split('"]')[0].replace('","','-')
                    hours = hours + '; ' + 'Tue: ' + item.split('"Tuesday":["')[1].split('"]')[0].replace('","','-')
                    hours = hours + '; ' + 'Wed: ' + item.split('"Wednesday":["')[1].split('"]')[0].replace('","','-')
                    hours = hours + '; ' + 'Thu: ' + item.split('"Thursday":["')[1].split('"]')[0].replace('","','-')
                    hours = hours + '; ' + 'Fri: ' + item.split('"Friday":["')[1].split('"]')[0].replace('","','-')
                    hours = hours + '; ' + 'Sat: ' + item.split('"Saturday":["')[1].split('"]')[0].replace('","','-')
                    hours = hours + '; ' + 'Sun: ' + item.split('"Sunday":["')[1].split('"]')[0].replace('","','-')
                    hours = hours.replace(': -',': Closed')
                    phone = phone.replace('\\r\\n',';').replace(';;',';').replace(';;',';').replace(';;',';').replace(';;',';').replace(';;',';')
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
