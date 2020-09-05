import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import ast

session = SgRequests()
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
    array = json.loads(r.content)
    for item in list(array.values()):
        website = 'hermes.com'
        name = item['eng-GB']['short_title'].strip()
        add = item['eng-GB']['street_address1'].strip()
        if '"street_address2":""' not in item['eng-GB']:
            add = add + ' ' + item['eng-GB']['street_address2'].strip()
        if '"street_address3":""' not in item['eng-GB']:
            add = add + ' ' + item['eng-GB']['street_address3'].strip()
        city = item['eng-GB']['city']
        state = item['eng-GB']['area'].strip()
        zc = item['eng-GB']['postal_code'].strip()
        phone = item['eng-GB']['store_phone_number'].strip()
        hours = '<MISSING>'
        if 'opening_hours' in item['eng-GB']:
            hrs = str(item['eng-GB']['opening_hours'])
            hrs = hrs.replace('[u','').replace('"]','').replace("'",'').replace(']','')
            if 'False' not in hrs:
                days = hrs.split(',')
                for day in days:
                    day = str(day)
                    days = ['','','Mon','Tue','Wed','Thu','Fri','Sat','Sun']
                    dayname = days[int(day[:1])]
                    text = dayname + ': ' + day.split(':')[1] + ':' + day.split(':')[2] + '-' + day.split(':')[3] + ':' + day.split(':')[4]
                    if hours == '<MISSING>':
                        hours = text
                    else:
                        hours = hours + '; ' + text
        hours = hours.replace(':0;',':00;')
        hours = hours.replace(':0-',':00-')
        if hours[-2:] == ':0':
            hours = hours + '0'
        country = item['eng-GB']['country']
        typ = 'Store'
        store = item['eng-GB']['store_id']
        lat = item['eng-GB']['geo_coordinates']['latitude']
        lng = item['eng-GB']['geo_coordinates']['longitude']
        if country == 'United States' or country == 'Canada':
            if country == 'United States':
                country = 'US'
            else:
                country = 'CA'
            if country == 'US' and ' ' in zc:
                state = zc.split(' ')[0]
                zc = zc.split(' ')[1]
            if country == 'CA' and ' ' in state:
                if 'British Columbia' in state:
                    zc = state.split('Columbia ')[1]
                    state = 'BC'
                else:
                    zc = state.split(' ',1)[1]
                    state = state.split(' ')[0]
            if city == 'Honolulu':
                state = 'HI'
            if city == 'Vancouver' and country == 'CA':
                state = 'BC'
            if ' O' in zc:
                zc = zc.replace(' O',' 0')
            state = state.replace('.','')
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
