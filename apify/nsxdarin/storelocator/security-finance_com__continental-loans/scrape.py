import csv
import urllib2
from sgrequests import SgRequests
import json

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
    url = 'https://www.security-finance.com/wpsl_stores-sitemap.xml'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if '<loc>https://www.securityfinance.com/locations/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        r2 = session.get(loc, headers=headers, verify=False)
        print('Pulling Location %s...' % loc)
        website = 'www.security-finance.com'
        typ = ''
        store = ''
        add = ''
        zc = ''
        state = ''
        city = ''
        country = ''
        name = ''
        phone = ''
        hours = ''
        NFound = False
        lat = '<MISSING>'
        lng = '<MISSING>'
        for line2 in r2.iter_lines():
            if '<h1 class="location-name">' in line2:
                typ = line2.split('<h1 class="location-name">')[1].split('<')[0]
            if '"name": "' in line2 and NFound is False:
                NFound = True
                name = line2.split('"name": "')[1].split('"')[0]
            if '"addressCountry": "' in line2:
                country = line2.split('"addressCountry": "')[1].split('"')[0]
                if country == 'USA':
                    country = 'US'
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"branchCode": "' in line2:
                store = line2.split('"branchCode": "')[1].split('"')[0]
            if '><tr><td>' in line2:
                days = line2.split('><tr><td>')
                for day in days:
                    if '</td></tr' in day:
                        dayname = day.split('<')[0]
                        hrs = day.split('</td><td>')[1].split('</td>')[0].replace('<time>','').replace('</time>','')
                        if hours == '':
                            hours = dayname + ': ' + hrs
                        else:
                            hours = hours + '; ' + dayname + ': ' + hrs
        if hours == '':
            hours = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
