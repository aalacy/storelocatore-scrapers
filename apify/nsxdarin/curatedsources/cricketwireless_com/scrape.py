import csv
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    PageFound = True
    x = 0
    while PageFound:
        x = x + 1
        print('Pulling Page %s...' % str(x))
        url = 'https://momentfeed-prod.apigee.net/api/llp/cricket.json?auth_token=IVNLPNUOBXFPALWE&center=37.9358,-122.3477&multi_account=false&name=Cricket+Wireless+Authorized+Retailer,Cricket+Wireless+Store&page=' + str(x) + '&pageSize=100&type=store'
        r = session.get(url, headers=headers)
        lines = r.iter_lines(decode_unicode=True)
        name = ''
        website = 'cricketwireless.com'
        loc = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = ''
        typ = ''
        lat = ''
        lng = ''
        hours = ''
        purl = ''
        PageFound = False
        for line in lines:
            if '"momentfeed_venue_id":' in line:
                PageFound = True
                name = ''
                website = 'cricketwireless.com'
                loc = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                country = 'US'
                store = ''
                typ = ''
                lat = ''
                lng = ''
                hours = ''
                purl = ''
            if '"corporate_id": "' in line:
                store = line.split('"corporate_id": "')[1].split('"')[0]
                add = next(lines).split('"address": "')[1].split('"')[0]
            if '"address_extended": "' in line:
                add = add + ' ' + line.split('"address_extended": "')[1].split('"')[0]
                add = add.strip()
            if '"locality": "' in line:
                city = line.split('"locality": "')[1].split('"')[0]
            if '"region": "' in line:
                state = line.split('"region": "')[1].split('"')[0]
            if '"postcode": "' in line:
                zc = line.split('"postcode": "')[1].split('"')[0]
            if '"phone": "' in line:
                phone = line.split('"phone": "')[1].split('"')[0]
            if '"llp_url": "' in line:
                purl = 'https://www.cricketwireless.com/stores' + line.split('"llp_url": "')[1].split('"')[0]
                if hours == '':
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                if '55555' in phone:
                    phone = '<MISSING>'
                if lat == '0.0':
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            if '"latitude": "' in line:
                lat = line.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line:
                lng = line.split('"longitude": "')[1].split('"')[0]
            if '"store_info": {' in line:
                typ = next(lines).split('"name": "')[1].split('"')[0]
                name = typ
            if hours == '' and '"store_hours": "' in line:
                hours = line.split('"store_hours": "')[1].split('"')[0]
                hours = hours.replace('1,','Mon: ').replace(';2,','; Tue: ')
                hours = hours.replace(';2,','; Tue: ')
                hours = hours.replace(';3,','; Wed: ')
                hours = hours.replace(';4,','; Thu: ')
                hours = hours.replace(';5,','; Fri: ')
                hours = hours.replace(';6,','; Sat: ')
                hours = hours.replace(';7,','; Sun: ')
                hours = hours.replace(',','-')

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
