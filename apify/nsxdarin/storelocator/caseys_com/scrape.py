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
    url = 'https://www.caseys.com/sitemap.xml'
    r = session.get(url, headers=headers)
    smurl = ''
    for line in r.iter_lines():
        if '<loc>https://www.caseys.com/medias/Store-en' in line:
            smurl = line.split('<loc>')[1].split('<')[0]
    r = session.get(smurl, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.caseys.com/general-store/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'caseys.com'
        typ = '<MISSING>'
        hours = ''
        country = 'US'
        name = ''
        city = ''
        add = ''
        state = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        store = loc.rsplit('/',1)[1]
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '"openingHours": [' in line2:
                g = next(lines)
                hours = g.split('"')[1]
            if '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"addressregion": "' in line2:
                state = line2.split('"addressregion": "')[1].split('"')[0]
            if '<div class="flex-grow-1 font-weight-bold">' in line2 and '</div>' not in line2:
                city = line2.split('<div class="flex-grow-1 font-weight-bold">')[1].split(',')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if typ == '' and '"@type": "' in line2:
                typ = line2.split('"@type": "')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
