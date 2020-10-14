import csv
from sgrequests import SgRequests
import sgzip
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
    for code in sgzip.for_radius(50):
        website = 'vpracingfuels.com'
        country = 'US'
        typ = 'Gas Station'
        url = 'https://vpracingfuels.com/wp-admin/admin-ajax.php?action=get_dealers_map_locations&zip_code=' + code + '&user_lat=&user_lng=&dealers=383'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if 'data-title=\\"' in line:
                items = line.split('data-title=\\"')
                for item in items:
                    if 'city=\\"' in item:
                        store = '<MISSING>'
                        name = item.split('\\')[0]
                        add = item.split('data-address=\\"')[1].split('\\')[0]
                        city = item.split('city=\\"')[1].split('\\')[0]
                        state = city.split(',')[1].strip().split(' ')[0]
                        zc = city.rsplit(' ',1)[1]
                        city = city.split(',')[0]
                        loc = '<MISSING>'
                        lat = item.split('data-lat=\\"')[1].split('\\')[0]
                        lng = item.split('data-lng=\\"')[1].split('\\')[0]
                        hours = '<MISSING>'
                        phone = '<MISSING>'
                        info = name + '|' + add + '|' + city
                        if state == 'New':
                            state = 'New York'
                        if info not in locs and state != 'ON':
                            locs.append(info)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
