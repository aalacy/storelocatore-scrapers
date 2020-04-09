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
    locs = []
    url = 'https://www.trinity-health.org/hospitals-locations'
    r = session.get(url, headers=headers)
    Found = False
    for line in r.iter_lines():
        if '_children_1" role="menu">' in line:
            Found = True
        if Found and '</ul>' in line:
            Found = False
        if Found and '<li class="navbar_6' in line:
            locs.append('http://www.trinity-health.org/' + line.split('a href="')[1].split('"')[0])
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        print('Pulling Region %s...' % loc)
        for line2 in r2.iter_lines():
            if '" src="https://www.google.com/maps/' in line2:
                gurl = line2.split('src="')[1].split('"')[0]
                r3 = session.get(gurl, headers=headers)
                for line3 in r3.iter_lines():
                    if ',[[[' in line3:
                        items = line3.split(',[[[')
                        for item in items:
                            if '"description' in item:
                                name = item.split('"name\\",[\\"')[1].split('\\')[0]
                                website = 'trinity-health.org'
                                add = item.split('"description\\",[\\"')[1].split('\\')[0]
                                csz = item.split('\\\\n')[1].split('\\')[0]
                                city = csz.split(',')[0]
                                state = csz.split(',')[1].strip().split(' ')[0]
                                zc = csz.rsplit(' ',1)[1]
                                phone = item.split('\\\\n')[2].split('\\')[0]
                                lat = item.split(',')[0]
                                lng = item.split(',')[1].split(']')[0]
                                typ = '<MISSING>'
                                country = 'US'
                                hours = '<MISSING>'
                                loc = '<MISSING>'
                                store = '<MISSING>'
                                if zc == '':
                                    zc = '<MISSING>'
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
