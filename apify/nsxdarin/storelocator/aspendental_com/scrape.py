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
    alllocs = []
    ids = []
    cities = []
    Found = False
    url = 'https://www.aspendental.com/find-an-office'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<li class="collection-index">A</li>' in line:
            Found = True
        if Found and '<li><a href="/dentist/' in line:
            lurl = 'https://www.aspendental.com' + line.split('<a href="')[1].split('"')[0]
            cities.append(lurl)
    print('Found %s Cities...' % str(len(cities)))
    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if '<li><a href="/dentist/' in line2:
                locurl = 'https://www.aspendental.com' + line2.split('<a href="')[1].split('"')[0]
                if locurl not in alllocs:
                    alllocs.append(locurl)
                    locs.append(locurl)
        for loc in locs:
            website = 'aspendental.com'
            typ = 'Office'
            hours = ''
            name = ''
            add = ''
            city = ''
            country = 'US'
            state = ''
            zc = ''
            phone = ''
            store = ''
            lat = ''
            lng = ''
            HFound = False
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '<div class="ssa-office-hours" style="background: #eeeeee;z-index:999999">' in line2:
                    HFound = True
                if HFound and '<div class="col-sm-8">' in line2:
                    HFound = False
                if HFound and '<p class="ssa-date">' in line2:
                    hrs = line2.split('<p class="ssa-date">')[1].split('<')[0]
                if HFound and '<p class="ssa-time">' in line2:
                    hrs = hrs + ': ' + line2.split('<p class="ssa-time">')[1].split('<')[0]
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
                if "'officeName':'" in line2:
                    name = line2.split("'officeName':'")[1].split("'")[0]
                    store = line2.split("'facilityNumber':'")[1].split("'")[0]
                    city = line2.split("'addressLocality':'")[1].split("'")[0]
                    state = line2.split(",'addressRegion':'")[1].split("'")[0]
                    zc = line2.split("'postalCode':'")[1].split("'")[0]
                    add = line2.split(",'streetAddress':'")[1].split("'")[0]
                    phone = line2.split("'telephone':'")[1].split("'")[0]
                if 'href="https://www.google.com/maps/dir/' in line2 and lat == '':
                    lat = line2.split('href="https://www.google.com/maps/dir/')[1].split(',')[0]
                    lng = line2.split('href="https://www.google.com/maps/dir/')[1].split(',')[1].split('/')[0]
            if hours == '':
                hours = '<MISSING>'
            if store not in ids:
                ids.append(store)
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
