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
    url = 'https://www.hilton.com/en/locations/homewood/'
    locs = []
    hids = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"ctyhocn":"' in line:
            items = line.split('"ctyhocn":"')
            for item in items:
                if ',"thumbImage":' in item:
                    hid = item.split('"')[0]
                    if hid not in hids:
                        hids.append(hid)
                        lurl = 'https://www.hilton.com/en/hotels/' + hid
                        locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        lat = ''
        lng = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        phone = ''
        store = ''
        hours = '<MISSING>'
        print('Pulling Location %s...' % loc)
        website = 'home2suites3.hilton.com'
        typ = 'Homewood Suites by Hilton | Extended Stay Hotels'
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"url": "https://www.hilton.com/en/hotels/' in line2:
                store = line2.split('"url": "https://www.hilton.com/en/hotels/')[1].split('-')[0]
            if '<meta name="og:title" content="' in line2:
                name = line2.split('<meta name="og:title" content="')[1].split('"')[0]
            if '<meta name="geo.position" content="' in line2:
                lat = line2.split('<meta name="geo.position" content="')[1].split(';')[0]
                lng = line2.split('<meta name="geo.position" content="')[1].split(';')[1].split('"')[0]
            if '"streetAddress": ' in line2:
                add = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
            if '"telephone": ' in line2:
                phone = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
            if '"addressLocality": ' in line2:
                city = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
            if '"addressRegion": ' in line2:
                state = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
            if '"addressCountry": ' in line2:
                country = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
                if country == 'USA':
                    country = 'US'
                if 'CA' in country:
                    country = 'CA'
            if '"postalCode": ' in line2:
                zc = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
            if '"latitude": ' in line2:
                lat = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
            if '"longitude": ' in line2:
                lng = line2.split(':')[1].split(',')[0].replace('"','').replace('"','').strip()
        if country == 'CA' or country == 'US':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
