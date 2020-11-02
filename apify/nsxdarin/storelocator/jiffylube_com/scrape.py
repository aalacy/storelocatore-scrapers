import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('jiffylube_com')



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
    for x in range(15, 65, 5):
        for y in range(-65, -175, -5):
            logger.info(('Pulling Coordinates %s-%s...' % (str(x), str(y))))
            url = 'https://www.jiffylube.com/api/locations?lat=' + str(x) + '&lng=' + str(y) + '&radius=250&state='
            r = session.get(url, headers=headers)
            if r.encoding is None: r.encoding = 'utf-8'
            for line in r.iter_lines(decode_unicode=True):
                if ',"postal_code":"' in line:
                    items = line.split(',"postal_code":"')
                    for item in items:
                        if '"country":"' in item:
                            zc = item.split('"')[0]
                            country = item.split('"country":"')[1].split('"')[0]
                            state = item.split(',"state":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            add = item.split('"address":"')[1].split('"')[0]
                            loc = 'https://www.jiffylube.com' + item.split('"_self":"')[1].split('"')[0]
                            store = loc.rsplit('/',1)[1]
                            phone = item.split('"phone_main":"')[1].split('"')[0]
                            name = item.split('"nickname":"')[1].split('"')[0]
                            website = 'jiffylube.com'
                            typ = '<MISSING>'
                            lat = item.split('"latitude":')[1].split(',')[0]
                            lng = item.split('"longitude":')[1].split('}')[0]
                            try:
                                hours = item.split('"hours":["')[1].split(']')[0].replace('","','; ').replace('"','')
                            except:
                                hours = '<MISSING>'
                            if hours == '':
                                hours = '<MISSING>'
                            if add != '' and loc not in locs:
                                locs.append(loc)
                                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
