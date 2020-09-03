import csv
from sgrequests import SgRequests
import time

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'sec-fetch-mode': 'navigate',
           'scheme': 'https',
           'method': 'GET',
           'sec-fetch-site': 'none',
           'sec-fetch-user': '?1',
           'authority': 'pier1.com'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.pier1.com/on/demandware.store/Sites-pier1_us-Site/default/LocalStore'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<a href="/on/demandware.store/Sites-pier1_us-Site/default/LocalStore?storeId=' in line:
            lurl = 'https://www.pier1.com' + line.split('href="')[1].split('"')[0]
            locs.append(lurl)
    print('Found %s Locations...' % str(len(locs)))
    for loc in locs:
        PFound = True
        time.sleep(3)
        print('Pulling Location %s...' % loc)
        website = 'pier1.com'
        typ = 'Store'
        store = loc.rsplit('=',1)[1]
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        while PFound:
            try:
                PFound = False
                r2 = session.get(loc, headers=headers)
                for line2 in r2.iter_lines():
                    line2 = str(line2.decode('utf-8'))
                    if '"name": "' in line2:
                        name = line2.split('"name": "')[1].split('"')[0]
                    if '"address":' in line2:
                        add = line2.split('"streetAddress":"')[1].split('"')[0]
                        state = line2.split('"addressRegion":"')[1].split('"')[0]
                        zc = line2.split('"postalCode":"')[1].split('"')[0]
                        city = line2.split('"addressLocality":"')[1].split('"')[0]
                    if '"telephone": "' in line2:
                        phone = line2.split('"telephone": "')[1].split('"')[0]
                    if '"openingHours": ["' in line2:
                        hours = line2.split('"openingHours": ["')[1].split('"]')[0].replace('","','; ')
                    if '<img src="https://maps.googleapis.com/' in line2:
                        lat = line2.split('|')[1].split(',')[0]
                        lng = line2.split('|')[1].split(',')[1].split('&')[0]
                if hours == '':
                    hours = '<MISSING>'
                country = 'US'
                if add != '':
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                PFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
