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
    states = []
    cities = []
    url = 'https://local.albertsons.com/index.html'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"links_directory" href="' in line:
            items = line.split('"links_directory" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(')')[0]
                    lurl = 'https://local.albertsons.com/' + item.split('"')[0]
                    if count == '1':
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if 'data-ya-track="links_directory" href="' in line2:
                items = line2.split('data-ya-track="links_directory" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(')')[0]
                        lurl = 'https://local.albertsons.com/' + item.split('"')[0]
                        if count == '1':
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if '<a class="Teaser-titleLink" href="../' in line2:
                items = line2.split('<a class="Teaser-titleLink" href="../')
                for item in items:
                    if 'data-ya-track="storename_directory">' in item:
                        lurl = 'https://local.albertsons.com/' + item.split('"')[0]
                        locs.append(lurl)
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 'albertsons.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = ''
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '-lead ContentBanner-title">' in line2:
                name = line2.split('-lead ContentBanner-title">')[1].split('<')[0]
                days = line2.split("days='[{")[1].split("}]'")[0].split('"day":"')
                try:
                    for day in days:
                        if '"intervals"' in day:
                            dname = day.split('"')[0]
                            if '"isClosed":true' in day:
                                hrs = dname + ': Closed'
                            else:
                                hrs = dname + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                            if hours == '':
                                hours = hrs
                            else:
                                hours = hours + '; ' + hrs
                except:
                    hours = '<MISSING>'
            if add == '' and 'address-street-1">' in line2:
                add = line2.split('address-street-1">')[1].split('<')[0]
                city = line2.split('"c-address-city">')[1].split('<')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('"postalCode">')[1].split('<')[0]
                phone = line2.split('id="phone-main">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if store == '' and 'href="https://www.albertsons.com/set-store.html?storeId=' in line2:
                store = line2.split('href="https://www.albertsons.com/set-store.html?storeId=')[1].split('&')[0]
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
