import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dominos_com')



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
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'https://pizza.dominos.com/' in line and '/home/sitemap' not in line:
            states.append(line.replace('\r','').replace('\n','').replace('\t','').strip())
    for state in states:
        Found = True
        logger.info(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'https://pizza.dominos.com/' in line2:
                if line2.count('/') == 4:
                    Found = False
                if Found:
                    locs.append(line2.replace('\r','').replace('\n','').replace('\t','').strip())
        logger.info(('%s Locations Found...' % str(len(locs))))
    for loc in locs:
        #logger.info('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
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
