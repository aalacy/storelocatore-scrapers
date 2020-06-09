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
    url = 'https://www.hyundai.co.uk/dealer-locator'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a href="/dealer/https://dealer.hyundai.co.uk/' in line:
            locs.append(line.split('dealer/')[1].split('"')[0])
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        print(loc)
        website = 'hyundai.co.uk'
        typ = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        country = 'GB'
        store = '<MISSING>'
        state = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        zc = ''
        phone = ''
        lines = r2.iter_lines()
        for line2 in lines:
            if '<div class="c-header__dealer-name">' in line2:
                name = line2.split('<div class="c-header__dealer-name">')[1].split('<')[0]
            if 'data-sales-lat="' in line2:
                lat = line2.split('data-sales-lat="')[1].split('"')[0]
            if 'data-sales-lng="' in line2:
                lng = line2.split('data-sales-lng="')[1].split('"')[0]
            if ' <a  href="tel:' in line2:
                phone = line2.split(' <a  href="tel:')[1].split('"')[0]
            if '<div class="c-footer__info-address">' in line2 and add == '':
                g = next(lines).strip().replace('\r','').replace('\n','').replace('\t','')
                if g.count(',') == 3:
                    add = g.split(',')[0].strip()
                    city = g.split(',')[1].strip()
                    state = g.split(',')[2].strip()
                    zc = g.split(',')[3].strip()
                if g.count(',') == 2:
                    add = g.split(',')[0].strip()
                    city = g.split(',')[1].strip()
                    state = '<MISSING>'
                    zc = g.split(',')[2].strip()
                if g.count(',') == 4:
                    add = g.split(',')[0] + ' ' + g.split(',')[1]
                    city = g.split(',')[2].strip()
                    state = g.split(',')[3].strip()
                    zc = g.split(',')[4].strip()
                if g.count(',') == 5:
                    add = g.split(',')[0] + ' ' + g.split(',')[1] + ' ' + g.split(',')[2]
                    city = g.split(',')[3].strip()
                    state = g.split(',')[4].strip()
                    zc = g.split(',')[5].strip()
                if g.count(',') == 6:
                    add = g.split(',')[0] + ' ' + g.split(',')[1] + ' ' + g.split(',')[2] + ' ' + g.split(',')[3]
                    city = g.split(',')[4].strip()
                    state = g.split(',')[5].strip()
                    zc = g.split(',')[6].strip()
                add = add.replace('  ',' ').replace('  ',' ').strip()
            if '<ul class="c-footer__ot">' in line2:
                hours = ''
            if '<li class="c-footer__ot-item">' in line2:
                hrs = line2.split('<li class="c-footer__ot-item">')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
