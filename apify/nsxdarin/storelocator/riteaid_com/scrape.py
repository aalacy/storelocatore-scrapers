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
    url = 'https://locations.riteaid.com/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'hreflang="en" href="https://locations.riteaid.com/locations/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            count = lurl.count('/')
            if count == 6:
                locs.append(lurl)
    print('Found %s Locations...' % str(len(locs)))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'riteaid.com'
        typ = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        country = 'US'
        zc = ''
        store = ''
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if 'data-storeid="' in line2:
                store = line2.split('data-storeid="')[1].split('"')[0]
            if 'id="location-name">' in line2:
                name = line2.split('id="location-name">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if " 'dimension4', '" in line2:
                add = line2.split(" 'dimension4', '")[1].split("'")[0]
                zc = line2.split("dimension5', '")[1].split("'")[0]
                state = line2.split("'dimension2', '")[1].split("'")[0]
                city = line2.split("'dimension3', '")[1].split("'")[0]
            if 'itemprop="telephone" id="telephone">' in line2:
                phone = line2.split('itemprop="telephone" id="telephone">')[1].split('<')[0]
            if hours == '' and "data-days='[{" in line2:
                days = line2.split("data-days='[{")[1].split(']}]')[0].split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        try:
                            hrs = day.split('"')[0] + ': ' + day.split(',"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        except:
                            hrs = day.split('"')[0] + ': Closed'
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if store != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
