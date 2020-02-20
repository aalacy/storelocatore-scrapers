import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    states = []
    url = 'https://pizza.dominos.com/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'https://pizza.dominos.com/' in line and '/home/sitemap' not in line:
            states.append(line.replace('\r','').replace('\n','').replace('\t','').strip())
    for state in states:
        Found = True
        print('Pulling State %s...' % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if 'https://pizza.dominos.com/' in line2:
                if line2.count('/') == 4:
                    Found = False
                if Found:
                    locs.append(line2.replace('\r','').replace('\n','').replace('\t','').strip())
        print('%s Locations Found...' % str(len(locs)))
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"branchCode":"' in line2:
                store = line2.split('"branchCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                name = "Domino's #" + store
                website = 'dominos.com'
                country = 'US'
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                typ = 'Store'
                hours = line2.split('"openingHours":["')[1].split('"]')[0].replace('","','; ')
                try:
                    phone = line2.split(',"telephone":"')[1].split('"')[0]
                except:
                    phone = '<MISSING>'
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
