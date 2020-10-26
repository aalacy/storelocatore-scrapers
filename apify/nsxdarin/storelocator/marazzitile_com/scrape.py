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
    url = 'https://locations.marazziusa.com/'
    r = session.get(url, headers=headers)
    website = 'marazzitile.com'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'data-galoc="State Index page' in line:
            lurl = line.split('href="')[1].split('"')[0]
            states.append(lurl)
    for state in states:
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'data-galoc="City Level' in line2:
                cities.append(line2.split('href="')[1].split('"')[0])
    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'data-gaact="Click_to_ViewLocalPage"' in line2:
                locs.append(line2.split('href="')[1].split('/"')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        store = loc.rsplit('/',1)[1]
        typ = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if 'property="business:contact_data:street_address" content="' in line2:
                add = line2.split('property="business:contact_data:street_address" content="')[1].split('"')[0]
            if 'property="business:contact_data:locality" content="' in line2:
                city = line2.split('property="business:contact_data:locality" content="')[1].split('"')[0]
            if 'property="business:contact_data:region" content="' in line2:
                state = line2.split('property="business:contact_data:region" content="')[1].split('"')[0]
            if 'property="business:contact_data:postal_code" content="' in line2:
                zc = line2.split('property="business:contact_data:postal_code" content="')[1].split('"')[0]
            if 'property="business:contact_data:phone_number" content="' in line2:
                phone = line2.split('property="business:contact_data:phone_number" content="')[1].split('"')[0]
            if 'place:location:latitude" content="' in line2:
                lat = line2.split('place:location:latitude" content="')[1].split('"')[0]
            if 'place:location:longitude" content="' in line2:
                lng = line2.split('place:location:longitude" content="')[1].split('"')[0]
            if '</style>' in line2:
                g = next(lines)
                g = str(g.decode('utf-8'))
                if '<h3>' in g:
                    typ = g.split('>')[1].split('<')[0]
            if 'var hoursArray' in line2:
                days = line2.split("Array('")
                for day in days:
                    if "')," in day:
                        hrs = day.split("'")[0] + ': ' + day.split(", '")[1].split("'")[0] + '-' + day.split(", '")[2].split("'")[0]
                        hrs = hrs.replace('CLOSED-CLOSED','Closed')
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '' or 'AM' not in hours:
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
