import csv
import urllib2
from sgrequests import SgRequests
import json
from sgzip import sgzip


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
    ids = []
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://site.becn.com/api-man/StoreLocation?facets=&lat=' + str(x) + '&long=' + str(y) + '&range=100'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '"name":"' in line:
                items = line.split('"name":"')
                for item in items:
                    if '"phone":"' in item:
                        name = item.split('"')[0]
                        store = '<MISSING>'
                        website = 'becn.com'
                        add = item.split('"addressLine1":"')[1].split('"')[0]
                        add2 = item.split('"addressLine2":"')[1].split('"')[0]
                        add = add + ' ' + add2
                        add = add.strip()
                        city = item.split('"city":"')[1].split('"')[0]
                        zc = item.split('"postalcode":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        country = item.split('"country":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split(',')[0]
                        hours = '<MISSING>'
                        loc = '<MISSING>'
                        phone = item.split('"phone":"')[1].split('"')[0]
                        if country == 'UNITED STATES':
                            country = 'US'
                        typ = item.split('"branchname":"')[1].split('"')[0]
                        storeinfo = name + '|' + add + '|' + lat
                        if phone == '':
                            phone = '<MISSING>'
                        if storeinfo not in ids and country == 'US':
                            ids.append(storeinfo)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
