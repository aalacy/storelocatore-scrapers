import csv
import urllib.request, urllib.error, urllib.parse
import requests
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('examone_com')



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
    stores = []
    for code in sgzip.for_radius(100):
        logger.info(('Pulling Zip %s...' % code))
        url = 'https://www.examone.com/locations/?zipInput=' + code + '&dist=100&submit=find+locations'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        lines = r.iter_lines(decode_unicode=True)
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
                            if ' 405 942' in add:
                                add = add.split(' 405 942')[0]
                            if ' 832-' in add:
                                add = add.split(' 832-')[0]
                            if ' 800-' in add:
                                add = add.split(' 800-')[0]
                            if ' 866-' in add:
                                add = add.split(' 866-')[0]
                            if ' 610-' in add:
                                add = add.split(' 610-')[0]
                            if ' 877' in add:
                                add = add.split(' 877')[0]
                            if ' Ofc#' in add:
                                add = add.split(' Ofc#')[0]
                            
                            yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
