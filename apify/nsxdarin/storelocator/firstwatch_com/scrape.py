import csv
import urllib2
import requests
import json
import time
from sgzip import sgzip

session = requests.Session()
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
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        time.sleep(1)
        print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        url = 'https://www.firstwatch.com/api/get_locations.php?latitude=' + x + '&longitude=' + y
        Found = True
        while Found:
            Found = False
            try:
                r = session.get(url, headers=headers)
                if '"city"' in r.content:
                    array = json.loads(r.content)
                    for item in array:
                        website = 'firstwatch.com'
                        hours = '<MISSING>'
                        name = item['name']
                        add = item['address'] + ' ' + item['address_extended']
                        add = add.strip()
                        phone = item['phone']
                        slug = item['slug']
                        surl = 'https://www.firstwatch.com/locations/' + slug
                        SFound = True
                        while SFound:
                            SFound = False
                            try:
                                r2 = session.get(surl, headers=headers)
                                for line2 in r2.iter_lines():
                                    if '<address>Open' in line2:
                                        hours = line2.split('<address>')[1].split('<')[0]
                                time.sleep(1)
                                typ = 'Restaurant'
                                city = item['city']
                                state = item['state']
                                zc = item['zip']
                                country = 'US'
                                store = item['corporate_id']
                                lat = item['latitude']
                                lng = item['longitude']
                                if store not in ids:
                                    ids.append(store)
                                    print('Pulling Store ID #%s...' % store)
                                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                            except:
                                SFound = True
            except:
                Found = False
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
