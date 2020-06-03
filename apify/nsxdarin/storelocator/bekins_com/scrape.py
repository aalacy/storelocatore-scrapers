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
    url = 'https://www.bekins.com/agent-sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.bekins.com/find-a-local-agent/agents/' in line and '<loc>https://www.bekins.com/find-a-local-agent/agents/<' not in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = '<MISSING>'
        print('Pulling Location %s...' % loc)
        website = 'bekins.com'
        typ = 'Agent'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<h2>' in line2:
                name = line2.split('<h2>')[1].split('<')[0].replace('\t','')
            if '<div class="agent-address">' in line2:
                g = next(lines)
                add = g.split('<')[0].strip().replace('\t','')
                g = next(lines)
                city = g.split(',')[0].strip().replace('\t','')
                state = g.split(',')[1].split('&nbsp')[0].strip().replace('\t','')
                zc = g.split('&nbsp;&nbsp;')[1].split('<')[0].strip().replace('\t','')
            if 'Phone:' in line2 and 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0].replace('/','')
        country = 'US'
        store = '<MISSING>'
        hours = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
