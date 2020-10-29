import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('amctheatres_com')



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
    cities = []
    locs = []
    url = 'https://www.amctheatres.com/movie-theatres'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'txt--tiny" href="/movie-theatres/' in line:
            items = line.split('txt--tiny" href="/movie-theatres/')
            for item in items:
                if '<div id="react-container">' not in item:
                    lurl = 'https://www.amctheatres.com/movie-theatres/' + item.split('"')[0]
                    cities.append(lurl)
    for city in cities:
        logger.info('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '><h3><a class="Link" href="' in line2:
                lurl = 'https://www.amctheatres.com' + line2.split('><h3><a class="Link" href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        logger.info('Pulling Location %s...' % loc)
        website = 'amctheatres.com'
        typ = '<MISSING>'
        hours = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = ''
        phone = '<MISSING>'
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'property="place:location:latitude" content="' in line2:
                lat = line2.split('property="place:location:latitude" content="')[1].split('"')[0]
                lng = line2.split('property="place:location:longitude" content="')[1].split('"')[0]
            if 'name="amc:theatre-name" content="' in line2:
                name = line2.split('name="amc:theatre-name" content="')[1].split('"')[0]
            if 'street_address" content="' in line2:
                add = line2.split('street_address" content="')[1].split('"')[0]
            if 'contact_data:locality" content="' in line2:
                city = line2.split('contact_data:locality" content="')[1].split('"')[0]
            if 'data:region" content="' in line2:
                state = line2.split('data:region" content="')[1].split('"')[0]
            if 'postal_code" content="' in line2:
                zc = line2.split('postal_code" content="')[1].split('"')[0]
            if '"amc:unit-number" content="' in line2:
                store = line2.split('"amc:unit-number" content="')[1].split('"')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
