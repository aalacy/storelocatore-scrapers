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
    url = 'https://www.allbirds.com/pages/stores'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    CFound = True
    website = 'allbirds.com'
    store = '<MISSING>'
    purl = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    typ = 'Store'
    for line in lines:
        if '<h2 class="Typography--secondary-heading Typography--with-margin">' in line:
            name = line.split('">')[1].split('<')[0]
            lat = '<MISSING>'
            lng = '<MISSING>'
            hours = '<MISSING>'
        if 'Auckland</h2>' in line:
            CFound = False
        if 'See Map</a></p>' in line and CFound:
            murl = line.split('href="')[1].split('"')[0]
            r2 = session.get(murl, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            lat = r2.url.split('@')[1].split(',')[0]
            lng = r2.url.split('@')[1].split(',')[1]
        if 'LOCATION</h3>' in line and CFound:
            g = next(lines)
            h = next(lines)
            add = g.split('">')[1].split('<')[0].strip()
            city = h.split(',')[0].strip()
            state = h.split(',')[1].strip().split(' ')[0].strip()
            zc = h.split('<')[0].rsplit(' ',1)[1].strip()
            country = 'US'
        if 'HOURS</h3>' in line and CFound:
            g = next(lines)
            h = next(lines)
            hours = g.split('">')[1].split('<')[0]
            if '</p>' in h:
                hours = hours + '; ' + h.split('<')[0]
        if 'paragraph">(' in line and CFound:
            phone = line.split('paragraph">')[1].split('<')[0]
            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
