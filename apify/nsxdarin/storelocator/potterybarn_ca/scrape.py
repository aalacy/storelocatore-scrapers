import csv
import urllib2
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
    website = 'potterybarn.ca'
    country = 'CA'
    loc = 'http://www.potterybarn.ca/edmonton-pb-ca'
    store = '<MISSING>'
    name = 'West Edmonton'
    add = '8882 170 Street Northwest Space 205/213'
    city = 'Edmonton'
    state = 'AB'
    zc = 'T5T 4J2'
    phone = '780-486-0349'
    typ = 'Pottery Barn'
    lat = '53.522'
    lng = '-113.623'
    hours = 'Mon: 10:00am-9:00pm, Tue: 10:00am-9:00pm, Wed: 10:00am-9:00pm, Thu: 10:00am-9:00pm, Fri: 10:00am-9:00pm, Sat: 10:00am-9:00pm, Sun: 11:00am-6:00pm'
    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    url = 'https://www.potterybarn.com/customer-service/store-locator.html?cm_type=fnav'
    r = session.get(url, headers=headers)
    storeinfo = []
    lines = r.iter_lines()
    for line in lines:
        if '<div class="store-card">' in line:
            next(lines)
            g = next(lines)
            surl = g.split('href="')[1].split('"')[0]
        if '<span itemprop="postalCode">' in line:
            pc = line.split('<span itemprop="postalCode">')[1].split('<')[0].strip()
            storeinfo.append(pc + '|' + surl)
    locs = []
    url = 'https://www.potterybarn.com/search/stores.json?brands=PB,PK,PT&lat=40.714&lng=-73.986&radius=10000'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['storeListResponse']['stores']:
        country = item['properties']['COUNTRY_CODE']
        store = item['properties']['STORE_NUMBER']
        website = 'potterybarn.ca'        
        lat = item['properties']['LATITUDE']
        lng = item['properties']['LONGITUDE']
        add = item['properties']['ADDRESS_LINE_1'] + ' ' + item['properties']['ADDRESS_LINE_2']
        add = add.strip()
        zc = item['properties']['POSTAL_CODE']
        phone = item['properties']['PHONE_NUMBER_FORMATTED']
        city = item['properties']['CITY']
        name = item['properties']['STORE_NAME']
        state = item['properties']['STATE_PROVINCE']
        stub = item['properties']['BRAND'].lower()
        if stub == 'pk' or stub == 'pt':
            stub = 'stores-' + stub
        else:
            stub = 'stores'
        loc = 'https://www.potterybarn.com/' + stub + '/' + country.lower() + '/' + state.lower() + '/' + city.lower().replace(' ','-') + '-' + name.lower().replace(' ','-') + '/'
        typ = item['properties']['BRAND'] + ' ' + item['properties']['STORE_TYPE']
        hours = 'Mon: ' + item['properties']['MONDAY_HOURS_FORMATTED']
        hours = hours + '; Tue: ' + item['properties']['TUESDAY_HOURS_FORMATTED']
        hours = hours + '; Wed: ' + item['properties']['WEDNESDAY_HOURS_FORMATTED']
        hours = hours + '; Thu: ' + item['properties']['THURSDAY_HOURS_FORMATTED']
        hours = hours + '; Fri: ' + item['properties']['FRIDAY_HOURS_FORMATTED']
        hours = hours + '; Sat: ' + item['properties']['SATURDAY_HOURS_FORMATTED']
        hours = hours + '; Sun: ' + item['properties']['SUNDAY_HOURS_FORMATTED']
        if country == 'CA' and 'PB ' in typ:
            for sitem in storeinfo:
                if zc == sitem.split('|')[0]:
                    loc = sitem.split('|')[1]
            typ = typ.replace('PB ','Pottery Barn')
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
