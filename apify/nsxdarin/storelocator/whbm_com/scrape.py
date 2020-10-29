import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('whbm_com')



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
    url = 'https://stores.whitehouseblackmarket.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://stores.whitehouseblackmarket.com/s/' in line:
            lurl = line.split('>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        stub = loc.rsplit('/',1)[1]
        jsonurl = 'https://whitehouse.brickworksoftware.com/en_US/api/v3/stores/' + stub
        logger.info(('Pulling Location %s...' % loc))
        website = 'whbm.com'
        typ = '<MISSING>'
        hours = ''
        r2 = session.get(jsonurl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            name = line2.split('"name":"')[1].split('"')[0]
            store = line2.split('"number":"')[1].split('"')[0]
            add = line2.split('"address_1":"')[1].split('"')[0]
            try:
                add = add + ' ' + line2.split('"address_2":"')[1].split('"')[0]
            except:
                pass
            city = line2.split('"city":"')[1].split('"')[0]
            state = line2.split('"state":"')[1].split('"')[0]
            zc = line2.split('"postal_code":"')[1].split('"')[0]
            country = line2.split('"country_code":"')[1].split('"')[0]
            try:
                phone = line2.split('"phone_number":"')[1].split('"')[0]
            except:
                phone = '<MISSING>'
            lat = line2.split(',"latitude":')[1].split(',')[0]
            lng = line2.split(',"longitude":')[1].split(',')[0]
            days = line2.split('{"start_time":"')
            for day in days:
                if 'display_start_time' in day:
                    if '"closed":false' in day:
                        hrs = day.split('"display_day":"')[1].split('"')[0] + ': ' + day.split('"display_start_time":"')[1].split('"')[0] + '-' + day.split('"display_end_time":"')[1].split('"')[0].strip()
                    else:
                        hrs = day.split('"display_day":"')[1].split('"')[0] + ': Closed'
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if country == 'US' or country == 'CA':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
