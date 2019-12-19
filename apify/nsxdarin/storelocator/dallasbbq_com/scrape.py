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
    url = 'https://www.dallasbbq.com'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    Found = True
    for line in r.iter_lines():
        if 'Order Online</a></li>' in line:
            Found = False
        if Found and '<a href="https://www.dallasbbq.com/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        print('Pulling Location %s...' % loc)
        website = 'dallasbbq.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<a href="tel:' in line2 and 'day' not in line2 and 'Hours' not in line2:
                phone = line2.split('<a href="tel:')[1].split('>')[1].split('<')[0]
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if '<h3 class="title text-cursive" style="text-align: center;"><strong>' in line2 or '<h3><strong>' in line2 and 'tel:' not in line2:
                add = line2.split('<strong>')[1].split('<')[0]
                g = next(lines).replace('</strong>','').replace('<strong>','')
                csz = g.split('<')[0].replace('(','').replace(')','')
                if ', ' in csz:
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.split(',')[1].strip().split(' ')[1]
                else:
                    city = '<MISSING>'
                    state = '<MISSING>'
                    zc = '<MISSING>'
            if '<span class="" style="display:block;clear:both;height' in line2 and 'Store Hours' not in line2:
                if hours == '':
                    hours = line2.split('<')[0].replace('&#8211;','-')
                else:
                    hours = hours + '; ' + line2.split('<')[0].replace('&#8211;','-')
        country = 'US'
        store = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        purl = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
