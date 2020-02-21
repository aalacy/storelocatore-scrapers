import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.trugreen.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.trugreen.com/local-lawn-care/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            if '-municipality</loc>' not in line and '-metro</loc>' not in line:
                if '/' in lurl.split('https://www.trugreen.com/local-lawn-care/')[1]:
                    locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        #print('Pulling Location %s...' % loc)
        website = 'trugreen.com'
        typ = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
                if ':' in name:
                    name = name.split(':')[0].strip()
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
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '<span class="col-3">' in line2:
                day = line2.split('<span class="col-3">')[1].split('<')[0]
            if '<span class="col-9">' in line2:
                hrs = line2.split('<span class="col-9">')[1].split('<')[0]
                if hours == '':
                    hours = day + ': ' + hrs
                else:
                    hours = hours + '; ' + day + ': ' + hrs
        country = 'US'
        store = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if city == '':
            city = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        if state == '':
            state = '<MISSING>'
        if add != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
