import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sgzip import sgzip


session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded',
           'host': 'www.whichwich.com',
           'origin': 'https://www.whichwich.com',
           'referer': 'https://www.whichwich.com/locations/'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    url = 'https://www.whichwich.com/locations/'
    for coord in sgzip.coords_for_radius(50):
        x = coord[0]
        y = coord[1]
        print(('Pulling Lat-Long %s,%s...' % (str(x), str(y))))
        payload = {'search': '',
                   'hdnLat': str(x),
                   'hdnLng': str(y),
                   'status': 'OK',
                   'hdnFormattedAddress': '',
                   'hdnFormattedState': ' '
                   }
        r = session.post(url, headers=headers, data=payload)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if 'value = [{"id":"' in line:
                items = line.split('"id":"')
                for item in items:
                    if '"api_id":"' in item:
                        website = 'whichwich.com'
                        name = item.split('"which_wich_store_name":"')[1].split('"')[0]
                        add = item.split('"address":"')[1].split('"')[0]
                        phone = item.split('"phone":"')[1].split('"')[0]
                        hrs1 = item.split('"store_hours_one":"')[1].split('"')[0]
                        hrs2 = item.split('"store_hours_two":"')[1].split('"')[0]
                        hrs3 = item.split('"store_hours_three":"')[1].split('"')[0]
                        hrs4 = item.split('"store_hours_four":"')[1].split('"')[0]
                        hours = hrs1
                        if hrs2 != '':
                            hours = hours + '; ' + hrs2
                        if hrs3 != '':
                            hours = hours + '; ' + hrs3
                        if hrs4 != '':
                            hours = hours + '; ' + hrs4
                        typ = 'Restaurant'
                        city = item.split('"store_city":"')[1].split('"')[0]
                        state = item.split('"store_state":"')[1].split('"')[0]
                        zc = item.split(',"store_zip":"')[1].split('"')[0]
                        country = 'US'
                        store = item.split('"')[0]
                        lat = item.split('"google_latitude":"')[1].split('"')[0]
                        lng = item.split('"google_longitude":"')[1].split('"')[0]
                        if store not in ids:
                            ids.append(store)
                            print(('Pulling Store ID #%s...' % store))
                            if '0' not in hours:
                                hours = '<MISSING>'
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
