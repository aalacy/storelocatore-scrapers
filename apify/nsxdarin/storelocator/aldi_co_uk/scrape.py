import csv
import urllib2
import requests
import time

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
    locs = []
    sm = ''
    url = 'https://www.aldi.co.uk/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.aldi.co.uk/sitemap/store' in line:
            sm = line.split('<loc>')[1].split('<')[0]
    r = session.get(sm, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.aldi.co.uk/store/' in line:
            locs.append(line.split('>')[1].split('<')[0])
    for loc in locs:
        time.sleep(3)
        print('Pulling Location %s...' % loc)
        website = 'aldi.co.uk'
        store = loc.split('s-uk-')[1]
        typ = 'Store'
        hours = ''
        country = 'GB'
        name = ''
        state = ''
        city = ''
        add = ''
        zc = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"seoData":{"name":"' in line2:
                name = line2.split('"seoData":{"name":"')[1].split('"')[0]
                try:
                    hours = line2.split('"openingHours":["')[1].split('"]')[0].replace('","','; ')
                except:
                    hours = '<MISSING>'
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = '<MISSING>'
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '{"store":' in line2:
                lat = line2.split('"lat":')[1].split(',')[0]
                lng = line2.split('"lng":')[1].split('}')[0]
        if hours == '':
            hours = '<MISSING>'
        phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
