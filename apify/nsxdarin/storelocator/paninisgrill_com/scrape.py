import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import re

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
    url = 'https://paninisgrill.com/locations/'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'mega-menu-link" href="https://paninisgrill.com/locations/' in line:
            items = line.split('mega-menu-link" href="https://paninisgrill.com/locations/')
            for item in items:
                lurl = 'https://paninisgrill.com/locations/' + item.split('"')[0]
                if ' ' not in lurl and lurl.count('/') == 5:
                    locs.append(lurl)
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        country = ''
        zc = ''
        phone = ''
        print(('Pulling Location %s...' % loc))
        website = 'paninisgrill.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' - ')[0]
            if add == '' and '<span class="elementor-icon-list-text">' in line2:
                csz = line2.split('<span class="elementor-icon-list-text">')[1].split('<br>(View')[0]
                if csz.count('<br>') == 1:
                    add = csz.split('<br>')[0]
                    city = csz.split('<br>')[1].split(',')[0]
                    state = csz.split('<br>')[1].split(',')[1].strip().split(' ')[0]
                    zc = csz.rsplit(' ',1)[1]
                else:
                    add = csz.split('<br>')[0] + ' ' + csz.split('<br>')[1]
                    city = csz.split('<br>')[2].split(',')[0]
                    state = csz.split('<br>')[2].split(',')[1].strip().split(' ')[0]
                    zc = csz.rsplit(' ',1)[1]
                country = 'US'
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'Hours</h5></div></div>' in line2:
                hrs = line2.split('Hours</h5></div></div>')[1].split('</div></div>')[0]
                cleanr = re.compile('<.*?>')
                hours = re.sub(cleanr, '', hrs)
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        hours = hours.replace('&#8211;','-')
        if 'Delivery' in hours:
            hours = hours.split('Delivery')[0]
        if 'Join' in hours:
            hours = hours.split('Join')[0]
        if 'Limited Menu' in hours:
            hours = hours.split('Limited Menu')[0]
        if 'NOW ' in hours:
            hours = hours.split('NOW')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
