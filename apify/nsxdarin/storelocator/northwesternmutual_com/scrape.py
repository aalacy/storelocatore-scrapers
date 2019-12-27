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
    locs = []
    url = 'https://www.northwesternmutual.com/sitemap-rep-pages.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.northwesternmutual.com/financial/advisor/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        website = 'northwesternmutual.com'
        typ = 'Financial Advisor'
        hours = '<MISSING>'
        add = ''
        city = ''
        phone = ''
        state = ''
        zc = ''
        lat = ''
        lng = ''
        store = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<h1>' in line2:
                name = line2.split('<h1>')[1].split('<')[0].strip()
            if 'profile--address>' in line2:
                add = line2.split('profile--address>')[1].split('<')[0].strip()
                csz = line2.split('profile--address>')[1].split('<br>')[1].split('<')[0].strip()
                city = csz.split(',')[0]
                country = 'US'
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.rsplit(' ',1)[1]
                try:
                    phone = line2.split('<a href=tel:')[1].split(' ')[0]
                except:
                    try:
                        phone = line2.split('<a href="tel:')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
            if '<a href="http://maps.google.com/maps?q=loc:' in line2:
                lat = line2.split('<a href="http://maps.google.com/maps?q=loc:')[1].split(',')[0]
                lng = line2.split('<a href="http://maps.google.com/maps?q=loc:')[1].split(',')[1].split('"')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
