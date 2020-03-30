import csv
import urllib2
from sgrequests import SgRequests
import sgzip
import time

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
    stores = []
    for code in sgzip.for_radius(100):
        print('Pulling Zip %s...' % code)
        url = 'https://www.examone.com/locations/?zipInput=' + code + '&dist=100&submit=find+locations'
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if 'var php_vars' in line:
                items = line.split('\\"qsl_id\\":\\"')
                for item in items:
                    if 'qsl_address' in item:
                        store = item.split('\\')[0]
                        name = 'ExamOne'
                        website = 'examone.com'
                        typ = '<MISSING>'
                        add = item.split('qsl_address\\":\\"')[1].split('\\')[0]
                        add = add + ' ' + item.split('"qsl_address2\\":\\"')[1].split('\\')[0]
                        city = item.split('"qsl_city\\":\\"')[1].split('\\')[0]
                        state = item.split('"qsl_state\\":\\"')[1].split('\\')[0]
                        zc = item.split('"qsl_zip\\":\\"')[1].split('\\')[0]
                        country = 'US'
                        phone = item.split('"qsl_phone\\":\\"')[1].split('\\')[0]
                        lurl = '<MISSING>'
                        add = add.strip()
                        lat = item.split('"qsl_latitude\\":\\"')[1].split('\\')[0]
                        lng = item.split('"qsl_longitude\\":\\"')[1].split('\\')[0]
                        hours = '<MISSING>'
                        if '(' in add:
                            if add.count('(') == 1:
                                typ = add.split('(')[1].split(')')[0]
                                add = add.split('(')[0].strip()
                            else:
                                typ = add.split('(')[2].split(')')[0]
                                add = add.split('(')[0].strip()
                        if store not in stores:
                            stores.append(store)
                            if phone == '':
                                phone = '<MISSING>'
                            yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
