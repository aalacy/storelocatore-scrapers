import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('purebarre_com')



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
    url = 'https://members.purebarre.com/api/brands/purebarre/locations?open_status=external&geoip='
    locs = []
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array['locations']:
        name = item['name']
        coming = item['coming_soon']
        lat = item['lat']
        lng = item['lng']
        if 'address2' in item:
            add = item['address'] + ' ' + str(item['address2'])
        add = add.strip()
        city = item['city']
        state = item['state']
        zc = item['zip']
        lurl = item['site_url']
        phone = item['phone']
        country = item['country_code']
        website = 'purebarre.com'
        typ = 'Location'
        hours = ''
        store = item['clubready_id']
        DFound = False
        if lurl is not None:
            logger.info(('Pulling Hours For %s...' % lurl))
            r2 = session.get(lurl, headers=headers)
            lines = r2.iter_lines(decode_unicode=True)
            for line2 in lines:
                if 'day&quot;:' in line2:
                    DFound = True
                    day = line2.split('&quot;')[1]
                    hrs = ''
                if '&quot;,' in line2 and DFound:
                    hrs = line2.split('&quot;')[1]
                    g = next(lines)
                    hrs = hrs + '-' + g.split('&quot;')[1]
                    if hours == '':
                        hours = day + ': ' + hrs
                    else:
                        hours = hours + '; ' + day + ': ' + hrs
        else:
            lurl = '<MISSING>'
            hours = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if coming is False:
            yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
