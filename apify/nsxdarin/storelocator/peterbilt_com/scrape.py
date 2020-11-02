import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('peterbilt_com')



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
    url = 'https://www.peterbilt.com/products-services/dealers'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'class="node node--type-dealership node--view-mode-teaser">' in line:
            locs.append('https://www.peterbilt.com' + line.split('about="')[1].split('"')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        website = 'peterbilt.com'
        typ = '<MISSING>'
        name = ''
        city = ''
        add = ''
        state = ''
        zc = ''
        country = ''
        store = ''
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<div class="field__item"><a href="tel:' in line2 and phone == '':
                phone = line2.split('<div class="field__item"><a href="tel:')[1].split('">')[1].split('<')[0]
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if 'property="latitude" content="' in line2:
                lat = line2.split('property="latitude" content="')[1].split('"')[0]
            if 'property="longitude" content="' in line2:
                lng = line2.split('property="longitude" content="')[1].split('"')[0]
            if 'class="address-line1">' in line2 and add == '':
                add = line2.split('class="address-line1">')[1].split('<')[0]
            if '<span class="locality">' in line2 and city == '':
                city = line2.split('<span class="locality">')[1].split('<')[0]
            if '<span class="administrative-area">' in line2 and state == '':
                state = line2.split('<span class="administrative-area">')[1].split('<')[0]
            if '<span class="postal-code">' in line2 and zc == '':
                zc = line2.split('<span class="postal-code">')[1].split('<')[0]
            if '<span class="country">U' in line2 and country == '':
                country = 'US'
            if '<span class="country">C' in line2 and country == '':
                country = 'CA'
            if '<span><span><span><span>' in line2:
                g = line2.replace('</span></span></span></span></span><span><span><span><span><span>','')
                hrs = g.split('<span><span><span><span>')[1].split('</span>')[0].replace('<strong>','').replace('</strong>','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '. - ' in line2 and '<span><span><span><span>' not in line2 and 'PM' in line2:
                if '<tr><td>' in line2:
                    hrs = line2.split('<td>')[1].split('</td>')[0].replace('<strong>','').replace('</strong>','')
                else:
                    try:
                        hrs = line2.split('<p>')[1].split('</p>')[0].replace('<strong>','').replace('</strong>','')
                    except:
                        hrs = line2.split('</span>')[0].strip().replace('\t','').replace('<strong>','').replace('</strong>','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<ul class="links"><li hreflang="en" data-drupal-link-system-path="node/' in line2:
                store = line2.split('<ul class="links"><li hreflang="en" data-drupal-link-system-path="node/')[1].split('"')[0]
        phone = phone.strip().replace('\t','')
        hours = hours.replace('&amp;','&').replace('<span>','')
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
