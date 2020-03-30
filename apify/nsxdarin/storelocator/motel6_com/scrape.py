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
    ids = []
    url = 'https://www.motel6.com/var/g6/hotel-rates.infinity.1.json'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"property_id":"' in line:
            items = line.split('"property_id":"')
            for item in items:
                if 'lastCreatedOrUpdated":"' not in item:
                    locs.append(item.split('"')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'motel6.com'
        purl = 'https://www.motel6.com/en/motels.' + loc + '.html?ncr=true'
        typ = ''
        hours = '<MISSING>'
        lurl = 'https://www.motel6.com/var/g6/hotel-information/en/' + loc + '.json'
        r2 = session.get(lurl, headers=headers)
        try:
            array = json.loads(r2.content)
            lat = array['latitude']
            lng = array['longitude']
            typ = array['brand_id']
            add = array['address'].encode('utf-8')
            zc = array['zip']
            city = array['city'].encode('utf-8')
            name = array['name'].encode('utf-8')
            state = array['state'].encode('utf-8')
            country = array['country']
            phone = array['phone']
            store = array['property_id']
            addinfo = add + city + state
            if addinfo not in ids:
                ids.append(addinfo)
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
