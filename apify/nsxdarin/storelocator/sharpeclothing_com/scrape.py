import csv
import urllib.request, urllib.error, urllib.parse
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
    coords = []
    url = 'https://sharpeclothing.com/our-stores/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<h3 class="post-name h5"><a href="https://sharpeclothing.com/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
        if 'var marker_object = cspm_new_pin_object' in line:
            cid = line.split('var marker_object = cspm_new_pin_object')[1].split(',')[1].strip().replace("'",'')
            clat = line.split('var marker_object = cspm_new_pin_object')[1].split(',')[2].strip()
            clng = line.split('var marker_object = cspm_new_pin_object')[1].split(',')[3].strip()
            coords.append(cid + '|' + clat + '|' + clng)
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        website = 'sharpeclothing.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        country = 'US'
        lat = '<MISSING>'
        lng = '<MISSING>'
        store = '<MISSING>'
        phone = ''
        zc = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' - ')[0]
                city = name.split(',')[0].strip()
                state = name.split(',')[1].strip()
            if 'href="https://goo.gl/maps/' in line2 and 'Get Directions' not in line2:
                add = line2.split('href="https://goo.gl/')[1].split('>')[1].split(city)[0].strip()
                if '&nbsp;' in line:
                    zc = line.split('&nbsp;')[1].split('<')[0]
            if 'a href="tel:' in line2:
                phone = line2.split('a href="tel:')[1].split('"')[0]
            if ',"post_id":"' in line2:
                store = line2.split(',"post_id":"')[1].split('"')[0]
        for coord in coords:
            if store == coord.split('|')[0]:
                lat = coord.split('|')[1]
                lng = coord.split('|')[2]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        if 'joplin-mo' in loc:
            add = '2702 Richard Joseph Boulevard Suite 109'
            state = 'MO'
            city = 'Joplin'
            phone = '(417) 553-0399'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
