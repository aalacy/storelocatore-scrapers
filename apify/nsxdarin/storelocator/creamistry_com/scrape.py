import csv
import urllib2
import requests

requests.packages.urllib3.disable_warnings()

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://creamistry.com/locations'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if 'class="stroe_link" href="' in line:
            lurl = 'https://creamistry.com/' + line.split('href="')[1].split('"')[0]
            if 'detail' not in lurl:
                locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        country = ''
        zc = ''
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'creamistry.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<h2 class="section-title">' in line2 and name == '':
                name = line2.split('<h2 class="section-title">')[1].split('<')[0]
            if '<h4>Address & Phone</h4>' in line2:
                g = next(lines)
                h = next(lines)
                add = g.split('>')[1].split('<')[0].strip()
                csz = g.split('<br')[1].split('>')[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
                country = 'US'
                phone = h.split('>')[1].split('<')[0]
            if 'var latitude = ' in line2:
                lat = line2.split('var latitude = ')[1].split(';')[0]
            if 'var longitude = ' in line2:
                lng = line2.split('var longitude = ')[1].split(';')[0]
            if 'Store Hours</h4>' in line2:
                g = next(lines)
                hours = g.split('">')[2].split('</strong>')[0]
                hours = hours.replace('<span>','').replace('</br>','').replace('</span>','').replace('  ',' ')
        if 'Soon' not in hours:
            if phone == '':
                phone = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
