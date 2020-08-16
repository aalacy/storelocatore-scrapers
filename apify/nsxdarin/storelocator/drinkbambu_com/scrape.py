import csv
from sgrequests import SgRequests
import json

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
    canada = ['AB','BC','ON','QC','PEI','SK','NB','NL','NS','PE']
    url = 'https://www.drinkbambu.com/find-bambu/'
    r = session.get(url, headers=headers)
    website = 'drinkbambu.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<a class="view-loc" href="' in line:
            items = line.split('<a class="view-loc" href="')
            for item in items:
                if '>View Location</a>' in item:
                    locs.append('https://www.drinkbambu.com' + item.split('"')[0])
    for loc in locs:
        print(loc)
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        store = '<MISSING>'
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        typ = '<MISSING>'
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<h1 itemprop="name">' in line2:
                name = line2.split('<h1 itemprop="name">')[1].split('<')[0]
            if '<span itemprop="address">' in line2:
                add = line2.split('<span itemprop="address">')[1].split('<span itemprop="addressLocality">')[0].replace('<br/>','').replace('</span>','').strip()
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('<span itemprop="postalCode">')[1].split('<')[0]
            if 'itemprop="telephone" content="' in line2:
                phone = line2.split('itemprop="telephone" content="')[1].split('">')[1].split('<')[0]
            if 'itemprop="openingHours">' in line2:
                hours = line2.split('itemprop="openingHours">')[1].split('<')[0]
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        name = name.replace('&#8217;',"'")
        if state in canada:
            country = 'CA'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
