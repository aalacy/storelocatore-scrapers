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
    ids = []
    urls = ['https://shellgsllocator.geoapp.me/api/v1/locations/within_bounds?sw%5B%5D=7.2&sw%5B%5D=-174.7&ne%5B%5D=25&ne%5B%5D=-148.1&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json',
            'https://shellgsllocator.geoapp.me/api/v1/locations/within_bounds?sw%5B%5D=49.7&sw%5B%5D=175&ne%5B%5D=68.3&ne%5B%5D=-131.8&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json'
            ]
    url = ''
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '{"id":"' in line:
                items = line.split('{"id":"')
                for item in items:
                    if '"name":"' in item:
                        name = item.split('"name":"')[1].split('"')[0]
                        lat = item.split('"lat":')[1].split(',')[0]
                        lng = item.split('"lng":')[1].split(',')[0]
                        add = item.split('"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"postcode":"')[1].split('"')[0]
                        country = item.split('"country_code":"')[1].split('"')[0]
                        phone = item.split('"telephone":"')[1].split('"')[0]
                        typ = item.split('"brand":"')[1].split('"')[0]
                        website = 'shell.us'
                        try:
                            loc = item.split('"website_url":"')[1].split('"')[0]
                        except:
                            loc = '<MISSING>'
                        store = loc.rsplit('/',1)[1].split('-')[0]
                        storeinfo = name + '|' + add + '|' + city + '|' + lat
                        hours = ''
                        if phone == '':
                            phone = '<MISSING>'
                        if storeinfo not in ids and country == 'US':
                            print('Pulling Store %s...' % name)
                            days = []
                            r2 = session.get(loc, headers=headers)
                            lines = r2.iter_lines()
                            rc = 0
                            dc = -1
                            try:
                                for line in lines:
                                    if '<div class="opening-times__cell">' in line:
                                        rc = rc + 1
                                        if rc <= 7:
                                            g = next(lines)
                                            days.append(g.strip().replace('\r','').replace('\n','').replace('\t',''))
                                        if rc >= 8:
                                            dc = dc + 1
                                            g = next(lines)
                                            days[dc] = days[dc] + ': ' + g.strip().replace('\r','').replace('\n','').replace('\t','')
                                for day in days:
                                    if hours == '':
                                        hours = day
                                    else:
                                        hours = hours + '; ' + day
                            except:
                                pass
                            if hours == '':
                                hours = '<MISSING>'
                            if phone == '':
                                phone = '<MISSING>'
                            name = name.replace('\\u0026','&')
                            add = add.replace('\\u0026','&')
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                            ids.append(storeinfo)

    url = ''
    for x in range(24, 50):
        for y in range(-66, -126, -1):
            lats = x
            latn = x + 1
            lnge = y
            lngw = y - 1
            print(str(x) + ',' + str(y))
            url = 'https://shellgsllocator.geoapp.me/api/v1/locations/within_bounds?sw%5B%5D=' + str(lats) + '&sw%5B%5D=' + str(lngw) + '&ne%5B%5D=' + str(latn) + '&ne%5B%5D=' + str(lnge) + '&selected=&autoload=true&travel_mode=driving&avoid_tolls=false&avoid_highways=false&avoid_ferries=false&corridor_radius=5&driving_distances=false&format=json'
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '{"id":"' in line:
                    items = line.split('{"id":"')
                    for item in items:
                        if '"name":"' in item:
                            name = item.split('"name":"')[1].split('"')[0]
                            lat = item.split('"lat":')[1].split(',')[0]
                            lng = item.split('"lng":')[1].split(',')[0]
                            add = item.split('"address":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            state = item.split('"state":"')[1].split('"')[0]
                            zc = item.split('"postcode":"')[1].split('"')[0]
                            country = item.split('"country_code":"')[1].split('"')[0]
                            phone = item.split('"telephone":"')[1].split('"')[0]
                            typ = item.split('"brand":"')[1].split('"')[0]
                            website = 'shell.us'
                            try:
                                loc = item.split('"website_url":"')[1].split('"')[0]
                            except:
                                loc = '<MISSING>'
                            storeinfo = name + '|' + add + '|' + city + '|' + lat
                            hours = ''
                            store = loc.rsplit('/',1)[1].split('-')[0]
                            if phone == '':
                                phone = '<MISSING>'
                            if storeinfo not in ids and country == 'US':
                                print('Pulling Store %s...' % name)
                                days = []
                                r2 = session.get(loc, headers=headers)
                                lines = r2.iter_lines()
                                rc = 0
                                dc = -1
                                try:
                                    for line in lines:
                                        if '<div class="opening-times__cell">' in line:
                                            rc = rc + 1
                                            if rc <= 7:
                                                g = next(lines)
                                                days.append(g.strip().replace('\r','').replace('\n','').replace('\t',''))
                                            if rc >= 8:
                                                dc = dc + 1
                                                g = next(lines)
                                                days[dc] = days[dc] + ': ' + g.strip().replace('\r','').replace('\n','').replace('\t','')
                                    for day in days:
                                        if hours == '':
                                            hours = day
                                        else:
                                            hours = hours + '; ' + day
                                except:
                                    pass
                                if hours == '':
                                    hours = '<MISSING>'
                                if phone == '':
                                    phone = '<MISSING>'
                                name = name.replace('\\u0026','&')
                                add = add.replace('\\u0026','&')
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                                ids.append(storeinfo)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
