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
    alllocs = []
    url = 'https://stores.homedepot.ca/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://stores.homedepot.ca/' in line and '.html' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            sid = lurl.rsplit('-',1)[1].split('.')[0]
            if len(sid) == 4 and '/bricolage-' not in lurl:
                locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'homedepot.ca'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        country = 'CA'
        lat = ''
        lng = ''
        store = loc.rsplit('-',1)[1].split('.')[0]
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if '<span class="location-name mb-5">' in line2:
                name = line2.split('<span class="location-name mb-5">')[1].split('<')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        hours = hours.replace('Su','Sun').replace(' Mo','; Mon').replace(' Tu','; Tue')
        hours = hours.replace(' We','; Wed')
        hours = hours.replace(' Th','; Thu')
        hours = hours.replace(' Fr','; Fri')
        hours = hours.replace(' Sa','; Sat')
        info = name + '|' + add
        if info not in alllocs:
            alllocs.append(info)
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
