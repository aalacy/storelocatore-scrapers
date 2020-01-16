import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.chick-fil-a.com/CFACOM.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.chick-fil-a.com/locations/' in line:
            items = line.split('<loc>https://www.chick-fil-a.com/locations/')
            for item in items:
                if '<?xml version="' not in item and 'browse' not in item:
                    locs.append('https://www.chick-fil-a.com/locations/' + item.split('<')[0])
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        country = ''
        typ = 'Restaurant'
        store = '<MISSING>'
        website = 'chick-fil-a.com'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        HFound = False
        for line2 in lines:
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' Location')[0]
            if '<p class="address">' in line2:
                g = next(lines)
                add = g.split(',')[0].strip().replace('\t','')
                city = g.split(',')[1].strip()
                state = g.split(',')[2].strip().split(' ')[0]
                zc = g.replace('\t','').replace('\r','').replace('\n','').strip().rsplit(' ',1)[1]
                country = 'US'
            if '<a href="https://www.google.com/maps/dir/Current+Location/' in line2:
                lat = line2.split('<a href="https://www.google.com/maps/dir/Current+Location/')[1].split(',')[0]
                lng = line2.split('<a href="https://www.google.com/maps/dir/Current+Location/')[1].split(',')[1].split('"')[0]
            if '<a href="tel:' in line2:
                phone = line2.split('">')[1].split('<')[0]
            if '<h3>Hours</h3>' in line2:
                HFound = True
            if HFound and '<div class="module amenities">' in line2:
                HFound = False
            if HFound and '<div class="flex">' in line2:
                g = next(lines)
                h = next(lines)
                hrs = g.split('>')[1].split('<')[0] + ': ' + h.split('>')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if phone == '':
            phone = '<MISSING>'
        if hours == '' or '-;' in hours:
            hours = '<MISSING>'
        if add != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
