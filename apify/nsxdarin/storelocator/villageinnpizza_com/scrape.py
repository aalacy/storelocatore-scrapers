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
    url = 'https://villageinnpizza.com/locations/'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'page"><a href="https://villageinnpizza.com/locations/' in line and 'food-truck' not in line:
            locs.append(line.split('href="')[1].split('"')[0])
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = ''
        lng = ''
        hours = '<MISSING>'
        country = 'US'
        zc = ''
        phone = ''
        print(('Pulling Location %s...' % loc))
        website = 'villageinnpizza.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' &#8211; Village')[0].replace('&#8211;','-')
            if "]['address']" in line2:
                add = line2.split('] = "')[1].split('"')[0].strip()
            if "]['long']" in line2:
                lng = line2.split('] = ')[1].split(';')[0].strip()
            if "]['lat']" in line2:
                lat = line2.split('] = ')[1].split(';')[0].strip()
            if '</strong></h3>' in line2:
                next(lines)
                g = next(lines)
                h = next(lines)
                city = g.split(',')[0]
                state = g.split(',')[1].strip().split(' ')[0]
                zc = g.split('<')[0].rsplit(' ',1)[1]
                phone = h.split('">')[1].split('<')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
