import csv
import urllib.request, urllib.error, urllib.parse
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
    for x in range(0, 15):
        print('Page %s...' % str(x))
        website = 'thebodyshop.com'
        country = 'CA'
        state = '<MISSING>'
        typ = '<MISSING>'
        url = 'https://api.thebodyshop.com/rest/v2/thebodyshop-ca/stores?fields=FULL&latitude=&longitude=&query=&lang=en_CA&curr=CAD&currentPage=' + str(x)
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode('utf-8'))
            if '"name" : "' in line and 'United' not in line:
                store = line.split('"name" : "')[1].split('"')[0]
            if '"displayName" : "' in line:
                name = line.split('"displayName" : "')[1].split('"')[0]
            if '"line1" : "' in line:
                hours = ''
                lat = ''
                lng = ''
                city = ''
                zc = ''
                phone = ''
                add = line.split('"line1" : "')[1].split('"')[0]
            if '"phone" : "' in line:
                phone = line.split('"phone" : "')[1].split('"')[0]
            if '"postalCode" : "' in line:
                zc = line.split('"postalCode" : "')[1].split('"')[0]
            if '"town" : "' in line:
                city = line.split('"town" : "')[1].split('"')[0]
            if '"latitude" : ' in line and 'source' not in line:
                lat = line.split('"latitude" : ')[1].split(',')[0]
            if '"longitude" : ' in line and 'source' not in line:
                lng = line.split('"longitude" : ')[1].strip().replace('\r','').replace('\n','')
            if '"closingTime" : ' in line:
                g = next(lines)
                g = str(g.decode('utf-8'))
                ct = g.split('"formattedHour" : "')[1].split('"')[0]
            if '"openingTime" : ' in line:
                g = next(lines)
                g = str(g.decode('utf-8'))
                ot = g.split('"formattedHour" : "')[1].split('"')[0]
            if '"weekDay" : "' in line:
                hrs = line.split('"weekDay" : "')[1].split('"')[0] + ': ' + ot + '-' + ct
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '"canonicalUrl" : "' in line:
                lurl = line.split('"canonicalUrl" : "')[1].split('"')[0]
            if '"storeImages" :' in line:
                if hours == '':
                    hours = '<MISSING>'
                if lat == '0.0':
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    for x in range(0, 15):
        print('Page %s...' % str(x))
        website = 'thebodyshop.com'
        country = 'US'
        state = '<MISSING>'
        typ = '<MISSING>'
        url = 'https://api.thebodyshop.com/rest/v2/thebodyshop-us/stores?fields=FULL&latitude=&longitude=&query=&lang=en_US&curr=USD&currentPage=' + str(x)
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode('utf-8'))
            if '"name" : "' in line and 'United' not in line:
                store = line.split('"name" : "')[1].split('"')[0]
            if '"displayName" : "' in line:
                name = line.split('"displayName" : "')[1].split('"')[0]
            if '"line1" : "' in line:
                hours = ''
                lat = ''
                lng = ''
                city = ''
                zc = ''
                phone = ''
                add = line.split('"line1" : "')[1].split('"')[0]
            if '"phone" : "' in line:
                phone = line.split('"phone" : "')[1].split('"')[0]
            if '"postalCode" : "' in line:
                zc = line.split('"postalCode" : "')[1].split('"')[0]
            if '"town" : "' in line:
                city = line.split('"town" : "')[1].split('"')[0]
            if '"latitude" : ' in line and 'source' not in line:
                lat = line.split('"latitude" : ')[1].split(',')[0]
            if '"longitude" : ' in line and 'source' not in line:
                lng = line.split('"longitude" : ')[1].strip().replace('\r','').replace('\n','')
            if '"closingTime" : ' in line:
                g = next(lines)
                g = str(g.decode('utf-8'))
                ct = g.split('"formattedHour" : "')[1].split('"')[0]
            if '"openingTime" : ' in line:
                g = next(lines)
                g = str(g.decode('utf-8'))
                ot = g.split('"formattedHour" : "')[1].split('"')[0]
            if '"weekDay" : "' in line:
                hrs = line.split('"weekDay" : "')[1].split('"')[0] + ': ' + ot + '-' + ct
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '"canonicalUrl" : "' in line:
                lurl = line.split('"canonicalUrl" : "')[1].split('"')[0]
            if '"storeImages" :' in line:
                if hours == '':
                    hours = '<MISSING>'
                if lat == '0.0':
                    lat = '<MISSING>'
                    lng = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
