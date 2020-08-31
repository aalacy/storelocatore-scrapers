import csv
from sgrequests import SgRequests
import sgzip
import us
import random

random.seed(123) 

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

CANADA_STATE_VARIATIONS = {'ab', 'alberta', 'bc', 'british columbia', 'mb', 'manitoba', 'nb', 'new brunswick', 'nl', 'newfoundland and labrador', 'nt', 'northwest territories', 'ns', 'nova scotia', 'nu', 'nunavut', 'on', 'ontario', 'pe', 'prince edward island', 'qc', 'quebec', 'sk', 'saskatchewan', 'yt', 'yukon', 'newfoundland', 'b.c.'}

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data(search):
    ids = set()
    code = search.next_zip()
    print("code: {}".format(code))
    locations = []
    while code:
        print('Pulling Zip Code %s...' % code)
        print('{} zip codes remaining'.format(search.zipcodes_remaining()))
        query_country = 'ca' if len(code) == 3 else 'us'
        url = 'https://maps.ckr.com/stores/search?brand=hardees&country=' + query_country + '&q=' + code + '&brand_id=1&zoom=8'
        coords = []
        r = session.get(url, headers=headers)
        for line in r.iter_lines(decode_unicode=True):
            if 'var storeJson' in line:
                items = line.split('"name":"')
                for item in items:
                    if '"distance":' in item:
                        lat = item.split('"lat":"')[1].split('"')[0]
                        lng = item.split('"lng":"')[1].split('"')[0]
                        zc = item.split('"postal_code":"')[1].split('"')[0]
                        if search.validate(float(lat), float(lng), zc): 
                            coords.append((lat, lng))
                        store = item.split('"id":')[1].split(',')[0]
                        if store in ids: continue
                        ids.add(store)
                        state = item.split('"state":"')[1].split('"')[0]
                        if us.states.lookup(state):
                            country = 'US'
                        elif state.strip().lower() in CANADA_STATE_VARIATIONS:
                            country = 'CA'
                        else:
                            continue
                        website = 'hardees.com/redburrito'
                        typ = item.split('"')[0]
                        name = item.split('"')[0]
                        add = item.split('"street":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        try:
                            phone = item.split('"phone":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        hrs = item.split('{"day":"')
                        hours = ''
                        for hr in hrs:
                            if '"time":"' in hr:
                                if hours == '':
                                    hours = hr.split('"')[0] + ': ' + hr.split('"time":"')[1].split('"')[0]
                                else:
                                    hours = hours + '; ' + hr.split('"')[0] + ': ' + hr.split('"time":"')[1].split('"')[0]
                        if hours == '':
                            hours = '<MISSING>'
                        loc = '<MISSING>'
                        locations.append([website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours])
        if not coords: print("zip returned no results: {}".format(search.current_zip))
        search.max_count_update(coords)
        code = search.next_zip()
    for location in locations:
        yield location

def scrape():
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    data = fetch_data(search)
    write_output(data)

scrape()
