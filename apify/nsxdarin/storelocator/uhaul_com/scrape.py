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
    url = 'https://www.uhaul.com/Locations/US_and_Canada/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<a href='/Locations/" in line:
            lurl = 'https://www.uhaul.com' + line.split("href='")[1].split("'")[0]
            states.append(lurl)
    for state in states:
        if 'Minnesota' in state:
            print('Pulling State %s...' % state)
            r2 = session.get(state, headers=headers)
            for line2 in r2.iter_lines():
                if "<a href='/Locations/" in line2:
                    lurl = 'https://www.uhaul.com' + line2.split("href='")[1].split("'")[0]
                    cities.append(lurl)
    for city in cities:
        coords = []
        alllocs = []
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '"entityNum":"' in line2:
                items = line2.split('"lat":')
                for item in items:
                    if '"entityNum":"' in item:
                        lat = item.split(',')[0]
                        lng = item.split('"long":')[1].split(',')[0]
                        pid = item.split('"entityNum":"')[1].split('"')[0]
                        coords.append(pid + '|' + lat + '|' + lng)
            if '<ul class="sub-nav ">' in line2:
                next(lines)
                g = next(lines)
                if 'href="' not in g:
                    g = next(lines)
                lurl = g.split('href="')[1].split('/"')[0]
                if 'http' not in lurl:
                    lurl = 'https://www.uhaul.com' + lurl
                enum = lurl.rsplit('/',1)[1]
                alllocs.append(lurl + '|' + enum)
        for location in alllocs:
            for place in coords:
                if location.split('|')[1] == place.split('|')[0]:
                    plat = place.split('|')[1]
                    plng = place.split('|')[2]
                    lurl = location.split('|')[0]
                    if lurl not in locs:
                        locs.append(lurl + '|' + plat + '|' + plng)
    for loc in locs:
        print('Pulling Location %s...' % loc.split('|')[0])
        website = 'uhaul.com'
        typ = ''
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        store = ''
        phone = ''
        lat = loc.split('|')[1]
        lng = loc.split('|')[2]
        lurl = loc.split('|')[0]
        store = lurl.rsplit('/',1)[1]
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            if '<small class="text-light">(' in line2 and 'all room' not in line2:
                typ = line2.split('<small class="text-light">(')[1].split(')')[0]
            if ',"addressRegion":"' in line2:
                state = line2.split(',"addressRegion":"')[1].split('"')[0]
                name = line2.split('"name":"')[1].split('"')[0]
                country = line2.split(',"addressCountry":"')[1].split('"')[0]
                if 'United' in country:
                    country = 'US'
                if 'Canada' in country:
                    country = 'CA'
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                hours = line2.split('"openingHours":')[1].split(',"aggregateRating')[0]
                hours = hours.replace('[','').replace(']','').replace('","','; ').replace('"','')
        if hours == '':
            hours = '<MISSING>'
        if typ == '':
            typ = 'U-Haul'
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
