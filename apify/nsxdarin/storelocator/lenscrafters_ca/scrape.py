import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('lenscrafters_ca')



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
    url = 'https://local.lenscrafters.ca/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://local.lenscrafters.ca/' in line and '.html' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            if lurl.count('/') == 5:
                locs.append(lurl)
    for loc in locs:
        logger.info('Pulling Location %s...' % loc)
        website = 'lenscrafters.ca'
        typ = '<MISSING>'
        hours = ''
        add = ''
        store = ''
        name = ''
        phone = ''
        city = ''
        state = ''
        zc = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'id="location-name" itemprop="name">' in line2 and name == '':
                name = line2.split('id="location-name" itemprop="name">')[1].split('<')[0]
            if 'id="location-name">' in line2 and name == '':
                name = line2.split('id="location-name">')[1].split('<')[0]
            if hours == '' and 'data-days=' in line2:
                days = line2.split('data-days=')[1].split('><')[0].split('"day":"')
                for day in days:
                    if 'interval' in day:
                        dname = day.split('"')[0]
                        if '[]' in day:
                            hrs = 'Closed'
                        else:
                            hrs = day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        if hours == '':
                            hours = dname + ': ' + hrs
                        else:
                            hours = hours + '; ' + dname + ': ' + hrs
            if store == '' and 'storeNumber=' in line2:
                store = line2.split('storeNumber=')[1].split('&')[0]
            if '<span class="c-address-street-1">' in line2 and add == '':
                add = line2.split('<span class="c-address-street-1">')[1].split('<')[0]
                if '<span class="c-address-street-2">' in line2:
                    add = add + ' ' + line2.split('<span class="c-address-street-2">')[1].split('<')[0]
                city = line2.split('itemprop="addressLocality" content="')[1].split('"')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                country = 'CA'
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if 'id="phone-main">' in line2 and phone == '':
                phone = line2.split('id="phone-main">')[1].split('<')[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if store == '':
            store = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
