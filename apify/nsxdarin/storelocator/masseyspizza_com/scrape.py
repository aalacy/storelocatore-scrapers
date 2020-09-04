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
    url = 'https://www.masseyspizza.com/locations/'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    state = 'OH'
    for line in lines:
        if 'South Carolina</span>' in line:
            state = 'SC'
        if '>Ohio Sports Bars' in line:
            state = 'OH'
        if '<div class="et_pb_text_inner"><p><strong>' in line:
            name = line.split('<div class="et_pb_text_inner"><p><strong>')[1].split('<')[0]
            add = ''
            city = name
            store = '<MISSING>'
            lat = ''
            lng = ''
            hours = ''
            country = 'US'
            zc = '<MISSING>'
            phone = ''
            website = 'masseyspizza.com'
            typ = 'Restaurant'
            loc = '<MISSING>'
            lat = '<MISSING>'
            lng = '<MISSING>'
            g = next(lines)
            if name == 'DELAWARE':
                city = 'Delaware'
                add = '219 S. Sandusky Street'
            else:
                if '</strong><br />' not in g:
                    add = g.split('<')[0]
                else:
                    city = g.split('<')[0]
                    add = next(lines).split('<')[0]
        if 'pm<' in line or 'idnight<' in line or 'am<' in line:
            hrs = line.split('<')[0]
            if hours == '':
                hours = hrs
            else:
                hours = hours + '; ' + hrs
            hours = hours.replace('&amp;','&')
        if '/@' in line:
            lat = line.split('/@')[1].split(',')[0]
            lng = line.split('/@')[1].split(',')[1]
            if ',+OH+' in line:
                zc = line.split(',+OH+')[1].split('/')[0]
        if '<a href="tel:+' in line:
            phone = line.split('<a href="tel:+')[1].split('"')[0]
        if '<a href="https://www.google.com/' in line:
            if 'AVE.' in city:
                city = 'COLUMBUS'
            if '/' in city:
                city = city.split('/')[0]
            if '261 Lincoln' in add:
                zc = '43230'
            if '!' in zc:
                zc = zc.split('!')[0]
            if '1951 E' in add or '261 Lincoln' in add:
                city = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
