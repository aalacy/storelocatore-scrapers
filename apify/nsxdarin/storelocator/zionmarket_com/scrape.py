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
    url = 'https://zionmarket.com/location'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '<p class="location-header-text">' in line:
            name = line.split('<p class="location-header-text">')[1].split('<')[0]
            add = ''
            city = '<MISSING>'
            state = '<MISSING>'
            store = '<MISSING>'
            lat = ''
            lng = ''
            hours = ''
            country = 'US'
            zc = '<MISSING>'
            phone = '<MISSING>'
            website = 'zionmarket.com'
            typ = 'Store'
            loc = '<MISSING>'
            g = next(lines)
            h = next(lines)
            i = next(lines)
            j = next(lines)
            add = g.split('>')[1].split('<')[0]
            if ', ' in h:
                city = h.split('>')[1].split(',')[0]
                state = h.split('>')[1].split(',')[1].strip().split(' ')[0]
                zc = h.split('>')[1].split(',')[1].strip().split(' ')[1].split('<')[0]
            phone = i.split('>')[1].split('<')[0]
            if 'Coming' not in j:
                hours = j.split('<p class="location-desc-text-3">')[1].split('</p>')[0].replace("<span class='time-emp'>",' - ').replace('</span>','')
        if '/@' in line:
            lat = line.split('@')[1].split(',')[0]
            lng = line.split('@')[1].split(',')[1]
            if hours != '':
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
