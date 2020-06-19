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
    url = 'https://www3.hilton.com/sitemapurl-hi-00000.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www3.hilton.com/en/hotels/' in line and 'accommodations/index.html' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    print(len(locs))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'hilton.com'
        typ = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<meta name="og:title" content="' in line2:
                name = line2.split('<meta name="og:title" content="')[1].split('"')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"productID":"' in line2:
                store = line2.split('"productID":"')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"addressCountry": "' in line2:
                country = line2.split('"addressCountry": "')[1].split('"')[0]
                if country == 'USA':
                    country = 'US'
                if country == 'Canada':
                    country = 'CA'
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
        hours = '<MISSING>'
        if country == 'US' or country == 'CA':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
