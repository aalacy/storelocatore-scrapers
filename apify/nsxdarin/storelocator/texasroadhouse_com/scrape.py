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
    url = 'https://www.texasroadhouse.com/locations/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'window.__locations__' in line:
            items = line.split('{"address1":"')
            for item in items:
                if '"address2"' in item:
                    add = item.split('"')[0]
                    if ',"address2":[]' not in item:
                        add = add + ' ' + item.split('"address2":"')[1].split('"')[0]
                    try:
                        city = item.split(',"city":"')[1].split('"')[0]
                    except:
                        city = '<MISSING>'
                    try:
                        state = item.split('"state":"')[1].split('"')[0]
                    except:
                        state = '<MISSING>'
                    country = item.split('"country":"')[1].split('"')[0]
                    try:
                        phone = item.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                    lat = item.split('"gps_lat":')[1].split(',')[0]
                    lng = item.split('"gps_lon":')[1].split(',')[0]
                    typ = 'Restaurant'
                    name = item.split(',"name":"')[1].split('"')[0]
                    if 'selectsite=' in item.lower():
                        store = item.lower().split('selectsite=')[1].split('"')[0]
                    else:
                        store = '<MISSING>'
                    try:
                        zc = item.split('"zip":"')[1].split('"')[0]
                    except:
                        zc = '<MISSING>'
                    website = 'texasroadhouse.com'
                    if name == '':
                        name = 'Texas Roadhouse'
                    if lat == '0':
                        lat = '<MISSING>'
                        lng = '<MISSING>'
                    if '"schedule":[]' in item:
                        hours = '<MISSING>'
                    else:
                        hours = 'Mon: ' + item.split('"day":"Monday","hours":')[1].split('"open":"')[1].split('"')[0] + '-' + item.split('"day":"Monday","hours":')[1].split('"close":"')[1].split('"')[0]
                        hours = hours + '; Tue: ' + item.split('"day":"Tuesday","hours":')[1].split('"open":"')[1].split('"')[0] + '-' + item.split('"day":"Tuesday","hours":')[1].split('"close":"')[1].split('"')[0]
                        hours = hours + '; Wed: ' + item.split('"day":"Wednesday","hours":')[1].split('"open":"')[1].split('"')[0] + '-' + item.split('"day":"Wednesday","hours":')[1].split('"close":"')[1].split('"')[0]
                        hours = hours + '; Thu: ' + item.split('"day":"Thursday","hours":')[1].split('"open":"')[1].split('"')[0] + '-' + item.split('"day":"Thursday","hours":')[1].split('"close":"')[1].split('"')[0]
                        hours = hours + '; Fri: ' + item.split('"day":"Friday","hours":')[1].split('"open":"')[1].split('"')[0] + '-' + item.split('"day":"Friday","hours":')[1].split('"close":"')[1].split('"')[0]
                        hours = hours + '; Sat: ' + item.split('"day":"Saturday","hours":')[1].split('"open":"')[1].split('"')[0] + '-' + item.split('"day":"Saturday","hours":')[1].split('"close":"')[1].split('"')[0]
                        hours = hours + '; Sun: ' + item.split('"day":"Sunday","hours":')[1].split('"open":"')[1].split('"')[0] + '-' + item.split('"day":"Sunday","hours":')[1].split('"close":"')[1].split('"')[0]
                    purl = 'https://www.texasroadhouse.com' + item.split(',"url":"')[1].split('"')[0].replace('\\','')
                    if country == 'USA':
                        country = 'US'
                    if country == 'CAN':
                        country = 'CA'
                    if store == '':
                        store = '<MISSING>'
                    if country == 'US' or country == 'CA' and ',"Opened":false' not in item:
                        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
