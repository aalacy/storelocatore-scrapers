import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    url = 'https://marathon.shotgunflat.com/data.txt'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        items = line.split('Marathon Gas - ')
        for item in items:
            if '|' in item:
                name = item.split('|')[0]
                add = item.split('|')[1]
                lat = item.split('|')[2]
                lng = item.split('|')[3]
                store = '<MISSING>'
                hours = '<MISSING>'
                website = 'marathonabrand.com'
                typ = '<MISSING>'
                city = item.split('|')[5]
                state = item.split('|')[6]
                country = 'US'
                phone = item.split('|')[8]
                zc = item.split('|')[7]
                loc = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
