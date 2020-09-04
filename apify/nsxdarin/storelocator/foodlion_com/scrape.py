import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for code in sgzip.for_radius(50):
        print(('Pulling Zip Code %s...' % code))
        url = 'https://www.foodlion.com/bin/foodlion/search/storelocator.json?zip=' + code + '&distance=5000&onlyPharmacyEnabledStores=false'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '{"result":"' in line:
                items = line.split('\\"id\\":')
                for item in items:
                    if '{"result":"' not in item:
                        website = 'foodlion.com'
                        typ = '<MISSING>'
                        country = 'US'
                        store = item.split(',')[0]
                        name = item.split('"title\\":\\"')[1].split('\\"')[0]
                        lat = item.split('"lat\\":')[1].split(',')[0]
                        lng = item.split(',\\"lon\\":')[1].split(',')[0]
                        hours = item.split('\\"hours\\":[\\"')[1].split('\\"]')[0].replace('\\",\\"','; ')
                        add = item.split('\\"address\\":\\"')[1].split('\\')[0].strip()
                        city = item.split('\\"city\\":\\"')[1].split('\\')[0]
                        state = item.split('\\"state\\":\\"')[1].split('\\')[0]
                        zc = item.split('"zip\\":\\"')[1].split('\\')[0]
                        phone = item.split('"phoneNumber\\":\\"')[1].split('\\')[0]
                        if store not in ids and store != '':
                            ids.append(store)
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
