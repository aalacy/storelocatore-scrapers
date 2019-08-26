import csv
import requests
import sgzip
import us

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data(search):
    ids = set()
    code = search.next_zip()
    print("code: {}".format(code))
    locations = []
    while code:
        print('Pulling Zip Code %s...' % code)
        print('{} zip codes remaining'.format(len(search.zipcodes)))
        url = 'https://maps.ckr.com/stores/search?brand=carlsjr&country=&q=' + code + '&brand_id=2&zoom=5'
        coords = []
        r = session.get(url, headers=headers)
        for line in r.iter_lines(decode_unicode=True):
            if 'var storeJson' in line:
                items = line.split('"name":"')
                for item in items:
                    if '"distance":' in item:
                        lat = item.split('"lat":"')[1].split('"')[0]
                        lng = item.split('"lng":"')[1].split('"')[0]
                        coords.append((lat, lng))
                        store = item.split('"id":')[1].split(',')[0]
                        if store in ids: continue
                        ids.add(store)
                        state = item.split('"state":"')[1].split('"')[0]
                        if us.states.lookup(state):
                            website = 'carlsjr.com'
                            typ = item.split('"')[0]
                            name = item.split('"')[0]
                            add = item.split('"street":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            zc = item.split('"postal_code":"')[1].split('"')[0]
                            try:
                                phone = item.split('"phone":"')[1].split('"')[0]
                            except:
                                phone = '<MISSING>'
                            country = 'US'
                            hrs = item.split('{"day":"')
                            hours = '<MISSING>'
                            for hr in hrs:
                                if '"time":"' in hr:
                                    if hours == '':
                                        hours = hr.split('"')[0] + ': ' + hr.split('"time":"')[1].split('"')[0]
                                    else:
                                        hours = hours + '; ' + hr.split('"')[0] + ': ' + hr.split('"time":"')[1].split('"')[0]
                            locations.append([website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours])
        if coords: search.update(coords)
        code = search.next_zip()
    for location in locations:
        yield location

def scrape():
    search = sgzip.ClosestNSearch()
    search.initialize()
    data = fetch_data(search)
    write_output(data)

scrape()
