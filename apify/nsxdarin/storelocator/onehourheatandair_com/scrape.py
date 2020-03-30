import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'http://onehourheatandair.com/sitemap.xml'
    sms = []
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<url><loc>https://www.onehourheatandair.com/locations/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'onehourheatandair.com'
        name = ''
        country = 'US'
        lat = '<MISSING>'
        lng = '<MISSING>'
        typ = 'Location'
        store = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        hours = '<MISSING>'
        phone = '<MISSING>'
        zc = '<MISSING>'
        city = '<MISSING>'
        state = '<MISSING>'
        add = '<MISSING>'
        for line2 in lines:
            if '<title>' in line2:
                name = line2.split('>')[1].split(' |')[0]
            if 'class="btn btn-primary">' in line2:
                phone = line2.split('tel:')[1].split('"')[0].strip()
        if name != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
