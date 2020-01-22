import csv
import urllib2
import requests

requests.packages.urllib3.disable_warnings()

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
    url = 'https://nativerootscannabis.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if '<loc>https://nativerootscannabis.com/locations/' in line:
            items = line.split('<loc>https://nativerootscannabis.com/locations/')
            for item in items:
                if 'xml version' not in item:
                    locs.append('https://nativerootscannabis.com/locations/' + item.split('<')[0])
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        country = ''
        zc = ''
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'nativerootsdispensary.com'
        typ = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<h1 data-testid="page-title" class="css-hcge3v">' in line2:
                name = line2.split('<h1 data-testid="page-title" class="css-hcge3v">')[1].split('<')[0]
            if '"@type":"PostalAddress",' in line2:
                add = line2.split(',"streetAddress":"')[1].split('"')[0]
                country = 'US'
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '<h5>' in line2:
                typ = line2.split('<h5>')[1].split('</h5>')[0].replace('<i>','').replace('</i>','')
            if '"openingHours":"' in line2:
                hours = line2.split('"openingHours":"')[1].split('"')[0]
        if 'broadway' in loc:
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 10:00-19:00'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
