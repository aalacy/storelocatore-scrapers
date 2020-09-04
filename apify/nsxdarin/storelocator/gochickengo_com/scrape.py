import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://gochickengo.com/pages/locations'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    hours = '<INACCESSIBLE>'
    website = 'gochickengo.com'
    store = '<MISSING>'
    typ = 'Store'
    state = ''
    phone = '<INACCESSIBLE>'
    country = 'US'
    name = 'Go Chicken Go'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '<a target="_blank" href="http://maps.google.com/maps?' in line:
            items = line.split('<a target="_blank" href="http://maps.google.com/maps?')
            for item in items:
                if ';q=' in item:
                    add = item.split(';q=')[1].split(',')[0].replace('+',' ').strip()
                    if 'kansas city' in add:
                        add = add.split(' kansas')[0]
                        city = 'Kansas City'
                        state = 'KS'
                        zc = '<MISSING>'
                    else:
                        city = item.split(';q=')[1].split(',')[1].replace('+',' ').strip()
                        state = item.split(';q=')[1].split(',')[2].split('&')[0].replace('+',' ').strip().split(' ')[0]
                        try:
                            zc = item.split(';q=')[1].split(',')[2].split('&')[0].replace('+',' ').strip().split(' ')[1]
                        except:
                            zc = '<MISSING>'
                    lat = item.split('sll=')[1].split(',')[0]
                    lng = item.split('sll=')[1].split(',')[1].split('&')[0]
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
