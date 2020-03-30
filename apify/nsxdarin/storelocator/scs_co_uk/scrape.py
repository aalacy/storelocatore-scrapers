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
    locs = []
    for x in range(50, 59):
        for y in range(-8, 1):
            print('%s-%s...' % (str(x), str(y)))
            url = 'https://www.scs.co.uk/on/demandware.store/Sites-SCS-Site/default/Stores-JSON?lat=' + str(x) + '&lng=' + str(y) + '&distance=25000'
            r = session.get(url, headers=headers)
            for item in json.loads(r.content):
                name = item['name']
                purl = 'https://www.scs.co.uk/stores/' + item['searchname'] + '.html'
                website = 'scs.co.uk'
                typ = '<MISSING>'
                add = item['address']
                city = item['city']
                state = '<MISSING>'
                country = 'GB'
                zc = item['postalCode']
                phone = item['phone']
                lat = item['lat']
                lng = item['lng']
                store = item['storeCode']
                hours = item['hours']
                if store == '':
                    store = '<MISSING>'
                if hours == '':
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                hours = hours.replace('"','').replace('[','').replace(']','').replace('{','').replace('}','').replace(',','; ').replace(' ;',';')
                if '0' not in store:
                    store = '<MISSING>'
                if add not in locs:
                    locs.append(add)
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
