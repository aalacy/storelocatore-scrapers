import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.homegoods.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.homegoods.com/store-details/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'homegoods.com'
        typ = 'Store'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<h1>' in line2:
                name = line2.split('<h1>')[1].split('<')[0]
            if '<h2>' in line2:
                g = next(lines)
                h = next(lines)
                add = g.split('<')[0].strip().replace('\t','')
                city = h.split(',')[0].strip().replace('\t','')
                state = h.split(',')[1].strip().split(' ')[0]
                zc = h.rsplit(' ',1)[1].strip().replace('\r','').replace('\n','')
            if '"Phone Number:Call">' in line2:
                phone = line2.split('"Phone Number:Call">')[1].split('<')[0].strip()
                g = next(lines)
                hours = g.split('<')[0].strip().replace('\r','').replace('\n','').replace('\t','')
        country = 'US'
        store = loc.rsplit('/',1)[1]
        lat = '<MISSING>'
        lng = '<MISSING>'
        if name == '':
            name = 'Home Goods'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
