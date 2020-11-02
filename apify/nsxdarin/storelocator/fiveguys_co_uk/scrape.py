import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fiveguys_co_uk')



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
    states = []
    niurl = 'https://www.fiveguys.co.uk/Northern-Ireland'
    url = 'https://restaurants.fiveguys.co.uk/index.html'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'All Five Guys Restaurants' not in item:
                    lurl = item.split('"')[0]
                    if 'http' not in lurl:
                        states.append('https://restaurants.fiveguys.co.uk/' + lurl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<a class="Teaser-contentWrapper" href="' in line2:
                items = line2.split('<a class="Teaser-contentWrapper" href="')
                for item in items:
                    if 'data-ya-track="businessname">' in item:
                        lurl = item.split('"')[0]
                        locs.append('https://restaurants.fiveguys.co.uk/' + lurl)
    r = session.get(niurl, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        website = 'fiveguys.co.uk'
        country = 'GB'
        state = 'Northern Ireland'
        if '<div class="col-xs-2 text-right">' in line:
            store = line.split('data-store-id="')[1].split('"')[0]
            typ = '<MISSING>'
            phone = line.split('data-store-telephone="')[1].split('"')[0]
            name = line.split('data-store-name="')[1].split('"')[0]
            lat = line.split('data-position="')[1].split(',')[0]
            lng = line.split('data-position="')[1].split(',')[1].strip().split('"')[0]
            if 'Belfast' in name:
                add = 'Victoria Square Shopping Centre  1 Victoria Square'
                city = 'Belfast'
                zc = 'BT1 4QG'
            if 'Boucher' in name:
                add = '32A Boucher Crescent'
                city = 'Belfast'
                zc = 'BT12 6HU'
            if 'Rushmere' in name:
                add = '3026 Rushmere Shopping Centre, Central Way'
                city = 'Craigavon'
                zc = 'BT64 1AA'
            hours = line.split('data-store-open="')[1].split('"')[0]
            loc = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    for loc in locs:
        logger.info(loc)
        loc = loc.replace('&#39;',"%27").replace('&amp;','%26')
        website = 'fiveguys.co.uk'
        country = 'GB'
        typ = '<MISSING>'
        store = ''
        name = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '"geomodifier":"' in line2:
                name = line2.split('"geomodifier":"')[1].split('"')[0]
            if 'meta itemprop="streetAddress" content="' in line2:
                add = line2.split('meta itemprop="streetAddress" content="')[1].split('"')[0]
                city = line2.split('itemprop="addressLocality" content="')[1].split('"')[0]
                state = '<MISSING>'
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                phone = line2.split('id="phone-main">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if '"location","id":"' in line2:
                store = line2.split('"location","id":"')[1].split('"')[0]
            if 'Store Hours:</h4>' in line2:
                days = line2.split('Store Hours:</h4>')[1].split("data-days=")[1].split("' data")[0].split('"day":"')
                for day in days:
                    if 'isClosed' in day:
                        if '"isClosed":true' in day:
                            hrs = day.split('"')[0] + ': Closed'
                        else:
                            hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        hours = hours.replace("'[{: Closed; ",'')
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
