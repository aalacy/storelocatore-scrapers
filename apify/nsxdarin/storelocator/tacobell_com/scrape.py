import csv
from sgrequests import SgRequests
import json

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
    alllocs = []
    locs = []
    states = []
    url = 'https://locations.tacobell.com/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<span class="Directory-listLinkText">' in line:
            items = line.split('<span class="Directory-listLinkText">')
            for item in items:
                if '"Directory-listLink" href="' in item:
                    surl = 'https://locations.tacobell.com/' + item.split('"Directory-listLink" href="')[1].split('"')[0]
                    states.append(surl)
    for state in states:
        cities = []
        locs = []
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<a class="Directory-listLink" href="' in line2:
                items = line2.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-ya-track="directory_links" data-count="(' in item:
                        curl = 'https://locations.tacobell.com/' + item.split('"')[0]
                        count = item.split('data-ya-track="directory_links" data-count="(')[1].split(')')[0]
                        if count == '1':
                            if curl not in alllocs:
                                alllocs.append(curl)
                                locs.append(curl)
                        else:
                            cities.append(curl)
        for city in cities:
            #print('Pulling City %s...' % city)
            r3 = session.get(city, headers=headers)
            for line3 in r3.iter_lines():
                line3 = str(line3.decode('utf-8'))
                if '<a data-ya-track="visit_site" href="../' in line3:
                    items = line3.split('<a data-ya-track="visit_site" href="../')
                    for item in items:
                        if 'View Page' in item:
                            lurl = 'https://locations.tacobell.com/' + item.split('"')[0]
                            if lurl not in alllocs:
                                alllocs.append(lurl)
                                locs.append(lurl)
        for loc in locs:
            #print('Pulling Location %s...' % loc)
            website = 'tacobell.com'
            typ = 'Restaurant'
            name = ''
            add = ''
            city = ''
            state = ''
            zc = ''
            country = 'US'
            store = ''
            phone = ''
            hours = ''
            lat = ''
            lng = ''
            r4 = session.get(loc, headers=headers, verify=False)
            for line4 in r4.iter_lines():
                line4 = str(line4.decode('utf-8'))
                if '"c_siteNumber":"' in line4 and store == '':
                    store = line4.split('"c_siteNumber":"')[1].split('"')[0]
                if 'property="og:title" content="' in line4:
                    name = line4.split('property="og:title" content="')[1].split(' |')[0]
                    add = line4.split('<span class="c-address-street-1">')[1].split('<')[0].strip()
                    city = line4.split('<span class="c-address-city">')[1].split('<')[0]
                    state = line4.split('itemprop="addressRegion">')[1].split('<')[0]
                    zc = line4.split('itemprop="postalCode">')[1].split('<')[0].strip()
                    phone = line4.split('itemprop="telephone" id="phone-main">')[1].split('<')[0]
                    lat = line4.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                    lng = line4.split('<meta itemprop="longitude" content="')[1].split('"')[0]
                    try:
                        hrs = line4.split('Drive-Thru Hours</h4>')[1].split("}]' data-")[0]
                        days = hrs.split('"day":"')
                        for day in days:
                            if '"intervals":' in day:
                                if hours == '':
                                    try:
                                        hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                    except:
                                        pass
                                else:
                                    try:
                                        hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                                    except:
                                        pass
                    except:
                        pass
            if hours == '':
                hours = '<MISSING>'
            if lat == '':
                lat = '<MISSING>'
            if lng == '':
                lng = '<MISSING>'
            if name != '':
                if store == '':
                    store = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
