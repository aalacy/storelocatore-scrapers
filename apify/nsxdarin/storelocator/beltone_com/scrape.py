import csv
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
    url = 'https://locations.beltone.com/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'href="http://locations.beltone.com/' in line:
            states.append(line.split('href="')[1].split('"')[0])
    for state in states:
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'linktrack="City index page - ' in line2:
                cities.append(line2.split('href="')[1].split('"')[0])
    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'Location page -' in line2:
                lurl = line2.split('href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
    print('Found %s Locations...' % str(len(locs)))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'beltone.com'
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
            line2 = str(line2.decode('utf-8'))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '"addressRegion":"' in line2:
                state = line2.split('"addressRegion":"')[1].split('"')[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"addressCountry":"' in line2:
                country = line2.split('"addressCountry":"')[1].split('"')[0]
            if '"latitude":' in line2:
                lat = line2.split('"latitude":')[1].split(',')[0]
            if '"longitude":' in line2:
                lng = line2.split(':')[1].strip().replace('\r','').replace('\n','').replace('\t','')
            if '"telephone":"' in line2:
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '"@id":"' in line2:
                store = line2.split('"@id":"')[1].split('"')[0]
            if 'hours_label">' in line2:
                day = line2.split('hours_label">')[1].split('<')[0]
            if '<span class="open' in line2 and 'hoursAlt' not in line2 and 'document.' not in line2:
                hrs = day + ' ' + line2.split('<span class="open')[1].split('"')[0] + '-' + line2.split('class="hideifclosed')[1].split('"')[0]
                if 'Closed' in hrs:
                    hrs = day + ' Closed'
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '' or '0' not in hours:
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        name = name.replace('&amp;','&')
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
