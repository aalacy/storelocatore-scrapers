import csv
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
    url = 'https://calibercollision.com/api/locations'
    r = session.get(url, headers=headers)
    website = 'calibercollision.com'
    typ = '<MISSING>'
    country = 'US'
    for item in json.loads(r.content)['entries']:
        name = item['title']
        add = item['address_info'][0]['address'].replace('"',"'")
        city = item['address_info'][0]['city']
        state = item['address_info'][0]['state_province']
        zc = item['address_info'][0]['zip']
        try:
            lat = item['address_info'][0]['latitude']
            lng = item['address_info'][0]['longitude']
        except:
            lat = '<MISSING>'
            lng = '<MISSING>'
        try:
            phone = item['address_info'][0]['phone']
        except:
            phone = '<MISSING>'
        loc = 'https://calibercollision.com/locate-a-caliber-collision-center/' + item['slug']
        try:
            store = item['location_id']
        except:
            store = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        hours = ''
        print(loc)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<span class="d-block pt-3 italic newtime">' in line2:
                g = next(lines)
                g = str(g.decode('utf-8'))
                if 'By Appointment Only' in g:
                    hours = 'By Appointment Only'
                else:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    hours = g.strip().replace('\t','').replace('\r','').replace('\n','')
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    hours = hours + '; ' + g.split('>')[1].strip().replace('\t','').replace('\r','').replace('\n','').replace('&amp;','&')
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
