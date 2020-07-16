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
    types = ['type0|Retail','type1|Commercial','type2|Commercial Maintenance','type3|Wholesale']
    url = 'https://www.pompstire.com/Locations'
    locs = []
    tels = []
    r = session.get(url, headers=headers, verify=False)
    lines = r.iter_lines()
    website = 'pompstire.com'
    hours = ''
    for line in lines:
        line = str(line.decode('utf-8'))
        if 'Use This Location</span><strong>' in line:
            name = line.split('Use This Location</span><strong>')[1].split('<')[0].replace('&apos;',"'")
            website = 'pompstire.com'
            loc = line.split("href='")[1].split("'")[0]
            hours = ''
        if 'class="loclisting' in line:
            typ = 'Store'
            typname = line.split('class="loclisting')[1].split('"')[0]
            if 'type0' in typname:
                typ = typ + ' Retail'
            if 'type1' in typname:
                typ = typ + ' Commercial'
            if 'type2' in typname:
                typ = typ + ' Commercial Maintenance'
            if 'type3' in typname:
                typ = typ + ' Wholesale'
        if "<img alt='Phone'" in line:
            phone = line.split('>')[1].strip().replace('\t','').replace('\r','').replace('\n','')
        if '<div class="locationInfo">' in line:
            next(lines)
            next(lines)
            g = next(lines)
            g = str(g.decode('utf-8'))
            h = next(lines)
            h = str(h.decode('utf-8'))
            if '1' not in g and '.' not in g and '0' not in g and '2' not in g and '7' not in g and ' St' not in g and '9' not in g and '3' not in g and '4' not in g and '5' not in g and '3' not in g and '6' not in g:
                g = h
                h = next(lines)
                h = str(h.decode('utf-8'))
            add = g.split('<')[0].strip().replace('\t','')
            city = h.split(',')[0].strip().replace('\t','')
            state = h.split(',')[1].strip().split(' ')[0]
            zc = h.strip().rsplit(' ',1)[1].replace('\t','').replace('\n','').replace('\r','')
            country = 'US'
            store = '<MISSING>'
        if 'day: ' in line:
            hrs = line.split('<')[0].strip().replace('\t','')
            if hours == '':
                hours = hrs
            else:
                hours = hours + '; ' + hrs
        if 'lon="' in line:
            lng = line.split('lon="')[1].split('"')[0]
            lat = line.split('lat="')[1].split('"')[0]
            loc = '<MISSING>'
            if 'tel:' in phone:
                phone = phone.split('tel:')[1].split("'")[0]
            if phone not in tels:
                tels.append(phone)
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
