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
        typ = ''
        store = '<MISSING>'
        website = 'chick-fil-a.com'
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if ',"telephone":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                phone = line2.split(',"telephone":"')[1].split('"')[0]
                typ = line2.split('"@type":"')[1].split('"')[0]
                country = line2.split('"addressCountry":"')[1].split('"')[0]
                add = line2.split(',"streetAddress":"')[1].split('"')[0]
                city = line2.split(',"addressLocality":"')[1].split('"')[0]
                state = line2.split(',"addressRegion":"')[1].split('"')[0]
                zc = line2.split(',"postalCode":"')[1].split('"')[0]
                add = line2.split(',"streetAddress":"')[1].split('"')[0]
                days = line2.split('"dayOfWeek":["')
                for day in days:
                    if '"closes":"' in day:
                        dopen = day.split('"opens":"')[1].split('"')[0]
                        dclose = day.split('"closes":"')[1].split('"')[0]
                        dopen = dopen.replace(':00:00',':00').replace(':30:00',':30')
                        dclose = dclose.replace(':00:00',':00').replace(':30:00',':30')
                        if 'Closed' in dopen:
                            dstring = 'Closed'
                        else:
                            dstring = dopen + '-' + dclose
                        if hours == '':
                            hours = day.split('"')[0] + ': ' + dstring
                        else:
                            hours = hours + '; ' + day.split('"')[0] + ': ' + dstring
            if 'data-distance-type="mi"' in line2 and 'data-lat' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-long="')[1].split('"')[0]
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
