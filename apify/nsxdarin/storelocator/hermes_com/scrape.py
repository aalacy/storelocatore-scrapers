import csv
import urllib2
import requests

session = requests.Session()
headers = {'Access-Token': '$/+8KDDU334$4a<C2M(6/<bhGyneX.e8i:6?&[57#n3h8=}z?*5Kc4W62;$BMLS#?P2Q7_PD~zxLK4x4_nPa8^HQ5H@4yMBLWev7y9iw754/k,biG6VxT33;tvg=}bcV',
           'Authorization': 'Basic aGVybWVzOndwSEt3ZldM',
           'Content-Type': 'application/json',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://stores.hermes.com/stores/get/(language)/eng-GB'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"short_title":"' in line:
            items = line.split('"short_title":"')
            for item in items:
                if '"street_address1":"' in item:
                    website = 'hermes.com'
                    name = item.split('"')[0].replace('\\u00e8','e')
                    add = item.split('"street_address1":"')[1].split('"')[0]
                    if '"street_address2":""' not in item:
                        add = add + ' ' + item.split('"street_address2":"')[1].split('"')[0]
                    if '"street_address3":""' not in item:
                        add = add + ' ' + item.split('"street_address3":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"area":"')[1].split('"')[0]
                    zc = item.split('"postal_code":"')[1].split('"')[0]
                    phone = item.split('"store_phone_number":"')[1].split('"')[0]
                    hours = ''
                    if '"opening_hours":' in item:
                        hours = item.split('"opening_hours":[')[1].split('"]')[0]
                    hours = hours.replace(':0:',':00:')
                    hours = hours.replace(',3:','; Tue: ')
                    hours = hours.replace(',4:','; Wed: ')
                    hours = hours.replace(',5:','; Thu: ')
                    hours = hours.replace(',6:','; Fri: ')
                    hours = hours.replace(',7:','; Sat: ')
                    hours = hours.replace(',8:','; Sun: ')
                    hours = hours.replace('"2:','Mon: ')
                    country = item.split('"country":"')[1].split('"')[0]
                    typ = 'Store'
                    store = item.split('"store_id":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split('}')[0]
                    if country == 'United States' or country == 'Canada':
                        if country == 'United States':
                            country = 'US'
                        else:
                            country = 'CA'
                        if country == 'US' and ' ' in zc:
                            zc = zc.split(' ')[1]
                            state = zc.split(' ')[0]
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
