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
    alllocs = []
    states = []
    url = 'https://www.enterprise.com/en/car-rental/locations/us.html'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<h3 class="state-title"><a class="heading-link" href="' in line:
            lurl = 'https://www.enterprise.com' + line.split('href="')[1].split('"')[0]
            states.append(lurl + '|US')
    url = 'https://www.enterprise.com/en/car-rental/locations/canada.html'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<h3 class="state-title"><a class="heading-link" href="' in line:
            lurl = 'https://www.enterprise.com' + line.split('href="')[1].split('"')[0]
            states.append(lurl + '|CA')
    for state in states:
        surl = state.split('|')[0]
        country = state.split('|')[1]
        locs = []
        r2 = session.get(surl, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<a href="https://www.enterprise.com/en/car-rental/locations/' in line2:
                lurl = line2.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    locs.append(lurl)
        for loc in locs:
            website = 'enterprise.com'
            name = ''
            add = ''
            city = ''
            state = ''
            zc = ''
            store = loc.rsplit('-',1)[1].split('.')[0]
            phone = ''
            typ = '<MISSING>'
            lat = ''
            lng = ''
            hours = ''
            print('Pulling Location %s...' % loc)
            r3 = session.get(loc, headers=headers)
            for line3 in r3.iter_lines():
                line3 = str(line3.decode('utf-8'))
                if '<meta property="og:title" content="' in line3:
                    name = line3.split('<meta property="og:title" content="')[1].split(' |')[0].replace('Car Rental ','')
                if '"streetAddress" : "' in line3:
                    add = line3.split('"streetAddress" : "')[1].split('"')[0]
                if '"addressLocality" : "' in line3:
                    city = line3.split('"addressLocality" : "')[1].split('"')[0]
                if '"addressRegion" : "' in line3:
                    state = line3.split('"addressRegion" : "')[1].split('"')[0]
                if '"postalCode" : "' in line3:
                    zc = line3.split('"postalCode" : "')[1].split('"')[0]
                if '"telephone" : "' in line3:
                    phone = line3.split('"telephone" : "')[1].split('"')[0].replace('+','')
                if '"latitude" : "' in line3:
                    lat = line3.split('"latitude" : "')[1].split('"')[0]
                if '"longitude" : "' in line3:
                    lng = line3.split('longitude" : "')[1].split('"')[0]
            if hours == '':
                hours = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
