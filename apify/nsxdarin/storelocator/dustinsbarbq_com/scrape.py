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
    url = 'http://dustinsbarbq.com/locations/'
    coords = []
    rc = -1
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '%22coordinates%22%3A%22' in line:
            items = line.split('%22coordinates%22%3A%22')
            for item in items:
                if 'data-elfsight-google-maps' not in item:
                    plat = item.split('%')[0]
                    plng = item.split('%2C%20')[1].split('%')[0]
                    coords.append(plat + '|' + plng)
        if '<h1 class="page-title">Dustin&#8217;s' in line:
            rc = rc + 1
            lat = coords[rc].split('|')[0]
            lng = coords[rc].split('|')[1]
            name = line.split('">')[1].split('<')[0].replace('&#8217;',"'")
            g = next(lines)
            h = next(lines)
            i = next(lines)
            phone = i.split('<')[0]
            add = g.split('>')[1].split('<')[0]
            country = 'US'
            if ',' in h:
                city = h.split(',')[0]
                state = h.split(',')[1].strip().split(' ')[0]
                zc = h.split(',')[1].strip().split(' ')[1].strip().split('<')[0]
            else:
                city = h.split(' ')[0]
                state = 'FL'
                zc = h.split('<')[0].strip().rsplit(' ',1)[1]
            website = 'dustinsbarbq.com'
            typ = 'Restaurant'
            loc = '<MISSING>'
            store = '<MISSING>'
            hours = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
