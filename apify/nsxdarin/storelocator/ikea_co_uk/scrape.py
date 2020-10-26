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
    url = 'https://www.ikea.com/gb/en/stores/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<p><a href="https://www.ikea.com/gb/en/stores/' in line and 'Bromley - Planning studio' not in line:
            locs.append(line.split('href="')[1].split('"')[0])
    PSFound = False
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        website = 'ikea.co.uk'
        typ = 'IKEA Store'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = '<MISSING>'
        zc = ''
        country = 'GB'
        store = '<MISSING>'
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        if 'planning-studios' in loc:
            typ = 'IKEA Planning Studio'
        if 'order-collection-point' in loc:
            typ = 'IKEA Order and Collection Point'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if 'planning-studios' in loc and '<h2><strong>' in line2 and 'FAQ' not in line2:
                name = line2.split('<strong>')[1].split('<')[0]
                if 'Bromley' in name:
                    add = '156-160 High Street'
                    city = 'Bromley'
                    zc = 'BR1 1HE'
                if 'Tottenham' in name:
                    add = '95 Tottenham Court Road, Bloomsbury'
                    city = 'London'
                    zc = 'W1T 4TW'
            if 'planning-studios' in loc and 'Opening Hours</strong></h3>' in line2:
                g = next(lines)
                hours = g.split('<p>')[1].split('</p>')[0].replace('&nbsp;',' ').replace('<strong>','').replace('</strong>','').replace('<br>','; ')
                if hours == '':
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if 'Address</strong>' in line2:
                g = next(lines)
                addinfo = g.split('>')[1].split('<')[0]
                if addinfo.count(',') == 2:
                    add = addinfo.split(',')[0].strip()
                    city = addinfo.split(',')[1].strip()
                    zc = addinfo.split(',')[2].strip()
                else:
                    add = addinfo.split(',')[0].strip() + ' ' + addinfo.split(',')[1].strip()
                    city = addinfo.split(',')[2].strip()
                    zc = addinfo.split(',')[3].strip()
            if ':00</strong>' in line2 and 'planning-studios' not in loc:
                hrs = line2.split('<p>')[1].split('</p>')[0].replace('</strong>','')
                hrs = hrs.replace('<strong>','').replace('&nbsp;',' ')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if 'planning-studios' not in loc:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
