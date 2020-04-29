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
    url = 'https://beacon-canada.com/Contact_Us.html'
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    name = ''
    hours = ''
    for line in lines:
        if 'Posi-' in line:
            name = ''
        if '<td width="33%"' in line and 'Posi-Slope' not in line and '><span style="font-weight: bold">' in line:
            name = line.split('><span style="font-weight: bold">')[1].split('<')[0]
            if '<strong>(' in line:
                name = name + ' ' + line.split('<strong>')[1].split('<')[0]
            if '<strong> (' in line:
                name = name + line.split('<strong>')[1].split('<')[0]
            g = next(lines).split('<')[0].strip().replace('\t','')
            h = next(lines).split('<')[0].strip().replace('\t','')
            add = g
            loc = '<MISSING>'
            website = 'beacon-canada.com'
            city = h.split(',')[0]
            zc = h.strip().rsplit(' ',2)[1] + ' ' + h.rsplit(' ',1)[1]
            country = 'CA'
            lat = '<MISSING>'
            lng = '<MISSING>'
            store = '<MISSING>'
            typ = '<MISSING>'
        if '<td scope="col"><span style="font-weight: bold">' in line and 'Posi-Slope' not in line and '><span style="font-weight: bold">' in line:
            name = line.split('><span style="font-weight: bold">')[1].split('<')[0]
            if '<strong>(' in line:
                name = name + ' ' + line.split('<strong>')[1].split('<')[0]
            if '<strong> (' in line:
                name = name + line.split('<strong>')[1].split('<')[0]
            g = next(lines).split('<')[0].strip().replace('\t','')
            h = next(lines).split('<')[0].strip().replace('\t','')
            add = g
            loc = '<MISSING>'
            website = 'beacon-canada.com'
            city = h.split(',')[0]
            zc = h.strip().rsplit(' ',2)[1] + ' ' + h.rsplit(' ',1)[1]
            country = 'CA'
            lat = '<MISSING>'
            lng = '<MISSING>'
            store = '<MISSING>'
            typ = '<MISSING>'
        if 'Locations </span>' in line:
            state = line.split('<h2><span style="font-weight: bold">')[1].split(' Locations')[0]
        if 'PH: (' in line:
            phone = line.split('PH: ')[1].split('<')[0]
        if '">Open:' in line:
            hours = line.split('">Open:')[1].split('</span>')[0].strip().replace('&#8226;','; ').replace('  ',' ')
        if 'Get Driving Directions' in line:
            hours = hours.replace('<span class="style3" style="font-weight: bold; font-size: 11px">','')
            hours = hours.replace(' ;',';')
            if name != '':
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
