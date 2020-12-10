import csv
from sgrequests import SgRequests
import sgzip

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
ids = []

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def scrape_url(url): 
    stores = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if '"name":"' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    lat = item.split('"lat":')[1].split(',')[0]
                    lng = item.split('"lng":')[1].split(',')[0]
                    add = item.split('"address":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"postcode":"')[1].split('"')[0]
                    country = item.split('"country_code":"')[1].split('"')[0]
                    phone = item.split('"telephone":"')[1].split('"')[0]
                    typ = item.split('"brand":"')[1].split('"')[0]
                    website = 'shell.us'
                    try:
                        loc = item.split('"website_url":"')[1].split('"')[0]
                    except:
                        loc = '<MISSING>'
                    hours = 'Open 24 Hours'
                    try:
                        store = loc.rsplit('/',1)[1].split('-')[0]
                    except:
                        store = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    if country == 'PR':
                        state = 'PR'
                        country = 'US'
                    if country == 'US' and loc != '<MISSING>':
                        if phone == '':
                            phone = '<MISSING>'
                        name = name.replace('\\u0026','&')
                        add = add.replace('\\u0026','&')
                        if loc != '<MISSING>':
                            if add == '':
                                add = '<MISSING>'
                            if zc == '':
                                zc = '<MISSING>'
                            poi = [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                            stores.append(poi)
    return stores


def parse_coords(stores): 
    result_coords = []
    for store in stores: 
        lat = store[-3]
        lng = store[-2]
        url = store[1]
        result_coords.append((lat,lng))
    return result_coords


def fetch_data():

    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US'])
    coord = search.next_coord()
    while coord:
        url = f"https://shellgsllocator.geoapp.me/api/v1/locations/nearest_to?lat={str(coord[0])}&lng={str(coord[1])}&selected=&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=true&format=json"
        stores = scrape_url(url)

        for store in stores: 
            name = store[2]
            add = store[3]
            city = store[4]
            store_num = store[-6]
            store_key = name + '|' + add + '|' + city + '|' + store_num
            if store_key not in ids: 
                ids.append(store_key)
                yield store 

        # Extract the latitude/longitude coordinates for each store
        result_coords = parse_coords(stores)
        search.max_count_update(result_coords)
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
