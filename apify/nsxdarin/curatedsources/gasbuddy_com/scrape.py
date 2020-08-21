import csv
from sgrequests import SgRequests
import time
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

states = ['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL',
          'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA',
          'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE',
          'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI',
          'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV',
          'WY']

provinces = ['AB','BC','MB','NB','NF','NS','NT','QC','PE','QC','SK']

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "open_status", "status", "branding_type", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    website = 'gasbuddy.com'
    for state in states:
        count = 0
        Found = True
        while Found:
            Found = False
            time.sleep(1)
            print(state + ': ' + str(count))
            url = 'https://www.gasbuddy.com/assets-v2/api/stations?regionCode=' + state + '&fuel=1&maxAge=0&cursor=' + str(count) + '&countryCode=US'
            r = session.get(url, headers=headers)
            count = count + 25
            try:
                for item in json.loads(r.content)['stations']:
                    Found = True
                    store = item['id']
                    country = item['address']['country']
                    name = item['name']
                    typ = item['item_type']
                    typ = str(typ).replace('[','').replace(']','').replace("'",'')
                    add = item['address']['line_1'] + ' ' + item['address']['line_2']
                    add = add.strip()
                    city = item['address']['locality']
                    state = item['address']['region']
                    zc = item['address']['postal_code']
                    phone = item['phone']
                    try:
                        hours = item['opening_hours']
                    except:
                        hours = '<MISSING>'
                    lat = item['latitude']
                    lng = item['longitude']
                    loc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    if zc == '':
                        zc = '<MISSING>'
                    os = item['open_status']
                    stat = item['status']
                    btype = ''
                    try:
                        for brand in item['brandings']:
                            if btype == '':
                                btype = brand['branding_type']
                            else:
                                btype = btype + ', ' + brand['branding_type']
                    except:
                        btype = '<MISSING>'
                    yield [website, loc, os, stat, btype, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                Found = False

    website = 'gasbuddy.com'
    for state in provinces:
        count = 0
        Found = True
        while Found:
            Found = False
            time.sleep(1)
            print(state + ': ' + str(count))
            url = 'https://www.gasbuddy.com/assets-v2/api/stations?regionCode=' + state + '&fuel=1&maxAge=0&cursor=' + str(count) + '&countryCode=CA'
            r = session.get(url, headers=headers)
            count = count + 25
            try:
                for item in json.loads(r.content)['stations']:
                    Found = True
                    store = item['id']
                    country = item['address']['country']
                    name = item['name']
                    typ = item['item_type']
                    typ = str(typ).replace('[','').replace(']','').replace("'",'')
                    add = item['address']['line_1'] + ' ' + item['address']['line_2']
                    add = add.strip()
                    city = item['address']['locality']
                    state = item['address']['region']
                    zc = item['address']['postal_code']
                    phone = item['phone']
                    try:
                        hours = item['opening_hours']
                    except:
                        hours = '<MISSING>'
                    lat = item['latitude']
                    lng = item['longitude']
                    loc = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    if zc == '':
                        zc = '<MISSING>'
                    os = item['open_status']
                    stat = item['status']
                    btype = ''
                    try:
                        for brand in item['brandings']:
                            if btype == '':
                                btype = brand['branding_type']
                            else:
                                btype = btype + ', ' + brand['branding_type']
                    except:
                        btype = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                Found = False

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
