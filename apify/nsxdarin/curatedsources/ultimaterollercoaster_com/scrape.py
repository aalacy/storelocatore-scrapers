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
    url = 'https://www.ultimaterollercoaster.com/themeparks/locator/'
    r = session.get(url, headers=headers)
    website = 'ultimaterollercoaster.com'
    Found = True
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<div id="footer">' in line:
            Found = False
        if Found and '<li><a href="/themeparks/' in line:
            if ' &ndash; ' not in line:
                lurl = 'https://www.ultimaterollercoaster.com' + line.split('"')[1].split('"')[0]
                locs.append(lurl)
            if ' &ndash; ' in line:
                if 'Canada' in line:
                    lurl = 'https://www.ultimaterollercoaster.com' + line.split('"')[1].split('"')[0]
                    locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        country = 'US'
        state = ''
        zc = ''
        add = ''
        city = ''
        name = ''
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<h1 class="new">' in line2:
                name = line2.split('<h1 class="new">')[1].split('<')[0].replace('&amp;','&')
            if '<p class="topblue">' in line2:
                mainloc = line2.split('<p class="topblue">')[1].split('</p')[0]
                city = mainloc.split(',')[0].strip()
                if 'Canada' in mainloc:
                    country = 'CA'
                if country == 'CA':
                    state = mainloc.split(',')[1].strip().split(' &ndash;')[0]
                else:
                    state = mainloc.split(',')[1].strip()
            if 'Park Location</h3>' in line2:
                g = next(lines)
                h = next(lines)
                g = str(g.decode('utf-8'))
                h = str(h.decode('utf-8'))
                csz = h.replace(' &ndash; Canada','').split('<')[0].strip()
                add = g.split('>')[1].split('<')[0]
                if country == 'CA':
                    zc = csz.rsplit(' ',2)[1]
                elif country == 'US':
                    zc = csz.split(',')[1].rsplit(' ',1)[1]
            if '<p>Phone:' in line2:
                phone = line2.split('<p>Phone:')[1].split('<')[0].strip()
            if 'latitude:' in line2:
                lat = line2.split('latitude:')[1].split(',')[0].strip()
            if 'longitude:' in line2:
                lng = line2.split('longitude:')[1].split(',')[0].strip()
            if country == 'CA' and 'html: "<div' in line2:
                zc = line2.split('</div>')[0].rsplit(',',1)[1]
                zc = zc.strip().replace('\t','')
        typ = '<MISSING>'
        store = '<MISSING>'
        hours = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
        if lng == '':
            lng = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if country == 'CA' or country == 'US':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
