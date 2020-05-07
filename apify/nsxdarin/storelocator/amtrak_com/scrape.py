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
    url = 'https://www.amtrak.com/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.amtrak.com/stations/' in line:
            items = line.split('<loc>https://www.amtrak.com/stations/')
            for item in items:
                if '<?xml' not in item:
                    lurl = 'https://www.amtrak.com/stations/' + item.split('<')[0]
                    locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'amtrak.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        lat = '<MISSING>'
        lng = '<MISSING>'
        phone = '<MISSING>'
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '"pageName": "' in line2:
                name = line2.split('"pageName": "')[1].split('"')[0]
            if '"hero-banner-and-info__card_station-type">' in line2:
                typ = line2.split('"hero-banner-and-info__card_station-type">')[1].split('<')[0]
            if '"hero-banner-and-info__card_block-address">' in line2 and add == '':
                add = line2.split('"hero-banner-and-info__card_block-address">')[1].split('<')[0]
                next(lines)
                g = next(lines)
                while '</span><br>-->' not in g:
                    g = next(lines)
                g = next(lines)
                while '"hero-banner-and-info__card_block-address">' not in g:
                    g = next(lines)
                csz = g.split('"hero-banner-and-info__card_block-address">')[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
            if '<a href="https://www.google.com/maps/dir//' in line2:
                lat = line2.split('<a href="https://www.google.com/maps/dir//')[1].split(',')[0]
                lng = line2.split('<a href="https://www.google.com/maps/dir//')[1].split(',')[1].split('"')[0]
        hurl = 'https://www.amtrak.com/content/amtrak/en-us/stations/bos.stationTabContainer.' + store.upper() + '.json'
        r3 = session.get(hurl, headers=headers)
        for line3 in r3.iter_lines():
            if '"type":"stationhours","rangeData":[{' in line3:
                days = line3.split('"type":"stationhours","rangeData":[{')[1].split('}]}]},')[0].split('"day":"')
                for day in days:
                    if 'timeSlot' in day:
                        hrs = day.split('"')[0] + ': ' + day.split('"timeSlot":"')[1].split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
