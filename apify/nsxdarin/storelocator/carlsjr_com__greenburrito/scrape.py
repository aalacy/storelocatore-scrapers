import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('carlsjr_com__greenburrito')



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
    url = 'https://carlsjr.com/sitemap.xml'
    r = session.get(url, headers=headers)
    website = 'carlsjr.com/greenburrito'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if ' <loc>https://carlsjr.com/locations/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        logger.info(loc)
        country = 'US'
        typ = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        store = '<MISSING>'
        lng = ''
        hours = ''
        RB = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('<')[0]
                add = name
            if '<span class="location-address">' in line2:
                csz = line2.split('<span class="location-address">')[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'lat: ' in line2:
                lat = line2.split('lat: ')[1].split(',')[0]
            if 'lng: ' in line2:
                lng = line2.split('lng: ')[1].strip().replace('\t','').replace('\r','').replace('\n','')
            if '<li><span>Mon' in line2:
                hours = line2.strip().replace('\t','').replace('\r','').replace('\n','')
                hours = hours.replace('</span></li><li><span>','; ').replace(' <span></span> ','-')
                hours = hours.replace('<li>','').replace('</li>','').replace('<span>','').replace('</span>','')
            if 'Green Burrito</span>' in line2:
                RB = True
        if RB is True:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
