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
    sm = 'https://local.uscellular.com/sitemap.xml'
    r = session.get(sm, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'sitemap.xml' in line:
            states.append(line.strip().replace('\r','').replace('\t','').replace('\n',''))
    for state in states:
        r2 = session.get(state, headers=headers)
        print(state)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'https://local.uscellular.com/' in line2:
                locs.append(line2.strip().replace('\r','').replace('\t','').replace('\n',''))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        lurl = 'https://uscc.koremuat.com//getStoreInfo?callback=jQuery191011573511012738757_1577812759166&id=' + loc
        website = 'uscellular.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        store = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<strong class="name">' in line2:
                g = next(lines)
                g = str(g.decode('utf-8'))
                name = g.strip().replace('\r','').replace('\t','').replace('\n','')
            if '<div class="street">' in line2:
                g = next(lines)
                g = str(g.decode('utf-8'))
                add = g.strip().replace('\r','').replace('\t','').replace('\n','')
            if '<div class="locality">' in line2:
                g = next(lines)
                g = str(g.decode('utf-8'))
                csz = g.strip().replace('\r','').replace('\t','').replace('\n','')
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if 'class="location-detail-phone-number">' in line2:
                phone = line2.split('tel:')[1].split('"')[0]
            if '"branchCode":"' in line2:
                store = line2.split('"branchCode":"')[1].split('"')[0]
            if '"openingHours":["' in line2:
                hours = line2.split('"openingHours":["')[1].split(']')[0].replace('","','; ').replace('"','')
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if 'a href' not in name:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
