import csv
import urllib2
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
    for x in range(0, 250):
        print(x)
        loc = 'http://www.trinity-health.org/body.cfm?id=21&action=detail&ref=' + str(x)
        r = session.get(loc, headers=headers)
        name = ''
        website = 'trinity-health.org'
        typ = '<MISSING>'
        add = ''
        state = ''
        city = ''
        zc = ''
        country = 'US'
        store = str(x)
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = '<MISSING>'
        for line in r.iter_lines():
            if '<dd id="locationName"><h2>' in line:
                name = line.split('<dd id="locationName"><h2>')[1].split('<')[0]
            if '<dd id="address">' in line:
                add = line.split('<dd id="address">')[1].split('<')[0]
                city = line.split('<br>')[1].split(',')[0]
                state = line.split('<br>')[1].split(',')[1].strip().split(' ')[0]
                zc = line.split('</dd>')[0].rsplit(' ',1)[1]
            if '<dd id="phone"><a href="tel:' in line:
                phone = line.split('<dd id="phone"><a href="tel:')[1].split('"')[0]
        if name != '':
            if zc == '':
                zc = '<MISSING>'
            if phone == '':
                phone = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
