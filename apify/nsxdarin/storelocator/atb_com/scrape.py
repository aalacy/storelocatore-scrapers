import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('atb_com')



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
    url = 'https://www.atb.com/resources/find-a-location/'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'window.branchData' in line:
            items = line.split('"name":"')
            for item in items:
                if 'window.branchData' not in item:
                    lurl = 'https://www.atb.com' + item.split('"url":"')[1].split('"')[0]
                    name = item.split('"')[0]
                    website = 'atb.com'
                    item.split('"')[0]
                    store = item.split('"Id":"')[1].split('"')[0]
                    add = item.split('"address":"')[1].split('\\')[0]
                    city = item.split('"cityName":"')[1].split('"')[0].title()
                    country = 'CA'
                    state = item.split('\\r\\n')[1].split(',')[1].strip().split(' ')[0]
                    zc = item.split('\\r\\n')[1].split(',')[1].strip().split(' ',1)[1].split('"')[0]
                    lat = item.split('"lat":')[1].split('}')[0]
                    lng = item.split('"lng":')[1].split(',')[0]
                    typ = item.split('"type":"')[1].split('"')[0]
                    hours = ''
                    phone = ''
                    r2 = session.get(lurl, headers=headers)
                    if r2.encoding is None: r2.encoding = 'utf-8'
                    logger.info(('Pulling Location %s...' % lurl))
                    lines = r2.iter_lines(decode_unicode=True)
                    for line2 in lines:
                        if '<a href="tel:' in line2:
                            phone = line2.split('<a href="tel:')[1].split('"')[0]
                        if '<li class="col-5">' in line2:
                            day = line2.split('<li class="col-5">')[1].split('<')[0]
                            g = next(lines)
                            if '>' not in g:
                                g = next(lines)
                            hrs = g.split('>')[1].split('<')[0]
                            if hours == '':
                                hours = day + ': ' + hrs
                            else:
                                hours = hours + '; ' + day + ': ' + hrs
                    if phone == '':
                        phone = '<MISSING>'
                    if hours == '':
                        hours = '<MISSING>'
                    if 'calgary-entrepreneur-centre' in lurl:
                        hours = 'Mon-Fri: 9:30AM-5PM; Sat: 9:30AM-4PM; Sun: Closed'
                    yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
