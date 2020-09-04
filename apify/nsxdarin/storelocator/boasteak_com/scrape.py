import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.boasteak.com'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<div class="dropdown-item w-dyn-item"><a href="/locations/' in line:
            items = line.split('<div class="dropdown-item w-dyn-item"><a href="/locations/')
            for item in items:
                if 'class="dropdown-link">' in item:
                    lurl = 'https://www.boasteak.com/locations/' + item.split('"')[0]
                    locs.append(lurl)
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        website = 'boasteak.com'
        typ = 'Restaurant'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<h1 class="location-title lightest">' in line2:
                name = line2.split('<h1 class="location-title lightest">')[1].split('<')[0]
                if ',' in line2.split('<h5 class="location-detail">')[1].split('<')[0]:
                    add = line2.split('<h5 class="location-detail">')[1].split(',')[0]
                    city = line2.split('<h5 class="location-detail">')[1].split(',')[1].strip()
                    state = line2.split('<h5 class="location-detail">')[1].split(',')[2].strip().split(' ')[0]
                    zc = line2.split('<h5 class="location-detail">')[1].split(',')[2].strip().split(' ')[1].split('<')[0]
                    phone = line2.split('<h5 class="location-detail">')[2].split('<')[0].replace('.','-')
                    country = 'US'
                    store = '<MISSING>'
                    hours = line2.split('<div class="location-hours w-richtext">')[1].split('</p><h5><strong>')[0].replace('</p><p>','; ').replace('<h5>','')
                    hours = hours.replace('</h5><p>',' - ').replace('</p>','; ')
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
