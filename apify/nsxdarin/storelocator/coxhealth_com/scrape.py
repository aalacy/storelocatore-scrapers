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
    url = 'https://www.coxhealth.com/our-hospitals-and-clinics/our-locations/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'View Location Info</a>' in line:
            lurl = 'https://www.coxhealth.com' + line.split('href="')[1].split('"')[0]
            locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'coxhealth.com'
        typ = '<MISSING>'
        hours = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        name = ''
        state = ''
        add = ''
        city = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        for line2 in lines:
            if 'open 24 hours' in line2.lower():
                hours = 'Open 24 Hours'
            if 'Hours</h3>' in line2:
                g = next(lines)
                if hours != 'Open 24 Hours':
                    hours = g.split('<p>')[1].split('<')[0]
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if 'Address</h3>' in line2:
                next(lines)
                next(lines)
                g = next(lines)
                csz = next(lines).replace('\r','').replace('\t','').replace('\n','').strip().replace('  ',' ')
                add = g.split('<')[0].strip().replace('\t','')
                if ',' in csz:
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.rsplit(' ',1)[1]
                else:
                    add = add + ' ' + csz
                    state = 'MO'
                    city = 'Springfield'
                    zc = '65807'
            if phone == '' and '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-lng="')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
