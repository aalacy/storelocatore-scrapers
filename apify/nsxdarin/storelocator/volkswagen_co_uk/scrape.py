import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('volkswagen_co_uk')



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
    urlhome = 'https://www.volkswagen.co.uk/app/dealersearch/vw-gb/en/Volkswagen%20Passenger%20Cars%20Search/+/53.98724/-1.0928/800/JCT600%20Volkswagen%20York/+/+/+'
    r = session.get(urlhome, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '%22id%5C%22:%5C%22' in line:
            items = line.split('%22id%5C%22:%5C%22')
            for item in items:
                if '%5C%22,%5C%22name%5C%22' in item:
                    lid = item.split('%')[0]
                    lat = item.split('%5C%22coordinates%5C%22:%5B')[1].split(',')[0]
                    lng = item.split('%5C%22coordinates%5C%22:%5B')[1].split(',')[1].split('%')[0]
                    locs.append(lid + '|' + lat + '|' + lng)
    for loc in locs:
        lat = loc.split('|')[1]
        lng = loc.split('|')[2]
        loc = loc.split('|')[0]
        logger.info(loc)
        url = 'https://cdn6.prodworksngwapi.de/sds/search/v2/dealers/' + loc + '?dv=1591269&tenant=v-gbr-dcc'
        r2 = session.get(url, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        website = 'volkswagen.co.uk'
        typ = '<MISSING>'
        country = 'GB'
        name = ''
        add = ''
        city = ''
        state = '<MISSING>'
        zc = ''
        store = loc
        phone = ''
        week = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        hours = ''
        lurl = ''
        for line2 in r2.iter_lines(decode_unicode=True):
            if ',"name":"' in line2:
                name = line2.split(',"name":"')[1].split('"')[0]
                add = line2.split('"street":"')[1].split('"')[0]
                city = line2.split(',"city":"')[1].split('"')[0]
                zc = line2.split('postalCode":"')[1].split('"')[0]
                try:
                    phone = line2.split(',"phoneNumber":"')[1].split('"')[0]
                except:
                    phone = '<MISSING>'
                lurl = line2.split('"website":"')[1].split('"')[0]
                try:
                    days = line2.split('"businessHours":{"days":[{')[1].split('}]}},')[0].split('"dayOfWeek":')
                    for day in days:
                        if '"from":"' in day:
                            daynum = int(day.split(',')[0])
                            hrs = day.split('"from":"')[1].split('"')[0] + '-' + day.split('"till":"')[1].split('"')[0]
                            hrs = week[daynum - 1] + ': ' + hrs
                            if hours == '':
                                hours = hrs
                            else:
                                hours = hours + '; ' + hrs
                except:
                    hours = '<MISSING>'
        if 'GL56 0XW' in zc:
            city = 'Moreton-In-Marsh'
            add = '<MISSING>'
        if 'Channel Islands Guernsey Volkswagen' in name:
            phone = '01481235441'
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
