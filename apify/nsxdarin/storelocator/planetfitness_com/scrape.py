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
    locs = []
    urls = ['https://www.planetfitness.com/sitemap.xml?page=1','https://www.planetfitness.com/sitemap.xml?page=2','https://www.planetfitness.com/sitemap.xml?page=3']
    for url in urls:
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '<loc>https://www.planetfitness.com/gyms/' in line:
                lurl = line.split('<loc>')[1].split('<')[0]
                if lurl not in locs:
                    locs.append(lurl)
    print(('Found %s Locations...' % str(len(locs))))
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        website = 'planetfitness.com'
        typ = 'Gym'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        store = ''
        phone = ''
        lat = ''
        lng = ''
        Found = False
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if "'clubID': '" in line2:
                store = line2.split("'clubID': '")[1].split("'")[0]
            if 'Club Hours</strong>' in line2:
                Found = True
            if Found and '<div>' in line2:
                Found = False
            if Found and '24' in line2:
                hours = '24 Hours, 7 Days A Week'
            if Found and 'Hours' not in line2:
                hrs = line2.replace('<p>','').split('<')[0].replace(',','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if 'name="title" content="' in line2:
                name = line2.split('name="title" content="')[1].split(' |')[0]
            if 'name="geo.position" content="' in line2:
                lat = line2.split('name="geo.position" content="')[1].split(',')[0]
                lng = line2.split('name="geo.position" content="')[1].split(',')[1].split('"')[0].strip()
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '"addressCountry": "' in line2:
                country = line2.split('"addressCountry": "')[1].split('"')[0]
                if country == 'United States':
                    country = 'US'
                if country == 'Canada':
                    country = 'CA'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if country == 'US' or country == 'CA':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
