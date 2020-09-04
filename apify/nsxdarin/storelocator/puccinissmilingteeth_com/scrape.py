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
    url = 'https://www.puccinispizzapasta.com'
    locs = []
    Found = False
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'INDIANAPOLIS, IN<br /></strong>' in line:
            line = line.replace('</a>Oaklandon','</a><strong>Oaklandon')
            items = line.split('<strong>')
            state = 'IN'
            city = 'Indianapolis'
            for item in items:
                if '<a href="https://goo.gl/maps/' in item:
                    website = 'puccinissmilingteeth.com'
                    name = item.split('<')[0]
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                    hours = '<MISSING>'
                    store = '<MISSING>'
                    typ = '<MISSING>'
                    lurl = '<MISSING>'
                    zc = '<MISSING>'
                    add = item.split('target="_blank">')[1].split('<')[0]
                    phone = item.split('href="tel:')[1].split('"')[0]
                    country = 'US'
                    name = name.replace(' at ','')
                    yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if 'LEXINGTON, KY<br /></strong>' in line:
            items = line.split('<strong>')
            state = 'KY'
            city = 'Lexington'
            for item in items:
                if '<a href="https://goo.gl/maps/' in item:
                    website = 'puccinissmilingteeth.com'
                    name = item.split('<')[0]
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                    hours = '<MISSING>'
                    store = '<MISSING>'
                    typ = '<MISSING>'
                    lurl = '<MISSING>'
                    zc = '<MISSING>'
                    add = item.split('target="_blank">')[1].split('<')[0]
                    phone = item.split('href="tel:')[1].split('"')[0]
                    country = 'US'
                    add = add.replace('&rsquo;',"'")
                    yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if 'WEST LAFAYETTE, IN<br /></strong>' in line:
            items = line.split('<strong>')
            state = 'IN'
            city = 'West Lafayette'
            for item in items:
                if '<a href="https://goo.gl/maps/' in item:
                    website = 'puccinissmilingteeth.com'
                    name = item.split('<')[0]
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                    hours = '<MISSING>'
                    store = '<MISSING>'
                    typ = '<MISSING>'
                    lurl = '<MISSING>'
                    zc = '<MISSING>'
                    add = item.split('target="_blank">')[1].split('<')[0]
                    phone = item.split('href="tel:')[1].split('"')[0]
                    country = 'US'
                    yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
