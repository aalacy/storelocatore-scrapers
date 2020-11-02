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
    cats = ['1|Hospitals','2|Urgent Care','17|Medical Offices','20|Wellness','21|Lab','19|Imaging']
    url = 'https://www.stjosephhealth.org/our-locations/'
    r = session.get(url, headers=headers)
    website = 'stjosephhealth.org'
    typ = '<MISSING>'
    country = 'US'
    loc = '<MISSING>'
    store = '<MISSING>'
    hours = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode('utf-8'))
        if '<div _category="' in line:
            catnum = line.split('<div _category="')[1].split('"')[0]
            for item in cats:
                if item.split('|')[0] == catnum:
                    typ = item.split('|')[1]
        if '<div class="location">' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            h = next(lines)
            h = str(h.decode('utf-8'))
            if '<h3>' in g:
                name = g.split('">')[1].split('<')[0]
            if '<h3>' in h:
                name = h.split('<h3>')[1].split('<')[0]
            Found = True
            while Found:
                g = next(lines)
                g = str(g.decode('utf-8'))
                if '<p>' in g and '</' not in g:
                    Found = False
            g = next(lines)
            g = str(g.decode('utf-8'))
            h = next(lines)
            h = str(h.decode('utf-8'))
            add = g.strip().replace('\r','').replace('\n','').replace('\t','')
            csz = h.split('>')[1].strip().replace('\r','').replace('\n','').replace('\t','')
            city = csz.split(',')[0]
            state = csz.split(',')[1].strip().split(' ')[0]
            zc = csz.rsplit(' ',1)[1]
        if 'Phone:' in line:
            if 'tel:' not in line:
                phone = '<MISSING>'
            else:
                phone = line.split('tel:')[1].split('"')[0]
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
