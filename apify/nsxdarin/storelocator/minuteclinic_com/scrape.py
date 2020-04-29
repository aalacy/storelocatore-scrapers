import csv
from sgrequests import SgRequests
import time
import random

session = SgRequests()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def fetch_data():

    locs = []
    states = []
    cities = []
    url = 'https://www.cvs.com/minuteclinic/clinic-locator/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if 'title="Locations in' in line:
            lurl = line.split('href="')[1].split('"')[0]
            states.append(lurl)

    for state in states:
        # print('Pulling State %s ...' % state)
        time.sleep(random.random()*5)
        r2 = session.get(state, headers=headers)

        for line2 in r2.iter_lines(decode_unicode=True):
            if 'title="Locations in' in line2:
                lurl = line2.split('href="')[1].split('"')[0]
                cities.append(lurl)

    for city in cities:
        # print('Pulling City %s ...' % city)
        time.sleep(random.random()*5)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'data-location-page="https://www.cvs.com/minuteclinic/clinic-locator/' in line2:
                locs.append(line2.split('data-location-page="')
                            [1].split('"')[0])

    for loc in locs:
        # print('Pulling Location %s ...' % loc)
        website = 'minuteclinic.com'
        typ = '<MISSING>'
        hours = ''
        name = 'Minute Clinic'
        add = ''
        city = ''
        country = 'US'
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        store = loc.rsplit('/', 1)[1].split('.')[0]

        time.sleep(random.random()*5)
        r2 = session.get(loc, headers=headers)

        if r2.url != loc and "cvs-pharmacy-address" in r2.url: 
          # page was redirected, meaning no minuteclinic at this location
          continue

        for line2 in r2.iter_lines(decode_unicode=True):
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[
                    1].split('"')[0].strip()
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
