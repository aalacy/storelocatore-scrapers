import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('saintalphonsus_org')



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
    url = 'https://www.saintalphonsus.org/sitemap-xml-locations'
    r = session.get(url, verify = False, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://www.saintalphonsus.org/location/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        rs = session.get(loc, headers=headers)
        website = 'saintalphonsus.org'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        country = 'US'
        typ = 'Office'
        store = ''
        lat = ''
        lng = ''
        for line2 in rs.iter_lines(decode_unicode=True):
            if '"Latitude\\\":' in line2:
                store = line2.split('"Id\\\\\\":')[1].split(',')[0]
                lat = line2.split('"Latitude\\\\\\":')[1].split(',')[0]
                lng = line2.split('"Longitude\\\\\\":')[1].split(',')[0]
                add = line2.split('"Address1\\\\\\":\\\\\\"')[1].split('\\')[0]
                city = line2.split('"City\\\\\\":\\\\\\"')[1].split('\\')[0]
                state = line2.split('"StateName\\\\\\":\\\\\\"')[1].split('\\')[0]
                zc = line2.split('PostalCode\\\\\\":\\\\\\"')[1].split('\\')[0]
                phone = line2.split('"Phone\\\\\\":\\\\\\"')[1].split('\\')[0]
                try:
                    hours = line2.split('"Values\\":[\\"')[1].split('\\"],')[0].replace('\\",\\"','; ')
                except:
                    hours = ''
            if 'class="ih-page-title" itemprop="name">' in line2:
                name = line2.split('class="ih-page-title" itemprop="name">')[1].split('<')[0]
        if 'Page Not' not in name:
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
