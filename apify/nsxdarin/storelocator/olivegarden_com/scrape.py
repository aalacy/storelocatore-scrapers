import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.olivegarden.com/en-locations-sitemap.xml'
    r = session.get(url, headers=headers)
    locs = []
    for line in r.iter_lines():
        if '<loc>https://www.olivegarden.com/locations/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                country = line2.split('"addressCountry":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                typ = line2.split('"@type":"')[1].split('"')[0]
                phone = line2.split(',"telephone":"')[1].split('"')[0]
                try:
                    lat = line2.split('"latitude":"')[1].split('"')[0]
                except:
                    lat = '<MISSING>'
                try:
                    lng = line2.split('"longitude":"')[1].split('"')[0]
                except:
                    lng = '<MISSING>'
                website = 'olivegarden.com'
                try:
                    store = line2.split('"url":"')[1].split('"')[0].rsplit('/',1)[1]
                except:
                    store = '<MISSING>'
                try:
                    hours = line2.split('"openingHours":["')[1].split('"]')[0].replace('","','; ')
                except:
                    hours = '<MISSING>'
                if store == '':
                    store = '<MISSING>'
                if add != '':
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
