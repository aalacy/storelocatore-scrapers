import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

logger = SgLogSetup().get_logger('dodge_ca')

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.dodge.ca/data/dealers/expandable-radius?brand=chrysler&longitude=-81.86942829543213&latitude=43.050732742209725&radius=9999'
    r = session.get(url, headers=headers)
    website = 'dodge.ca'
    typ = 'Dealer'
    country = 'CA'
    logger.info('Pulling Dealers...')
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '"code":"' in line:
            items = line.split('"code":"')
            for item in items:
                if ',"name":"' in item:
                    name = item.split(',"name":"')[1].split('"')[0]
                    store = item.split('"')[0]
                    logger.info('Pulling Dealer %s...' % store)
                    add = item.split('"address":"')[1].split('"')[0]
                    loc = 'https://www.chrysler.ca/en/dealers/' + store
                    city = item.split('"city":"')[1].split('"')[0]
                    zc = item.split('"zipPostal":"')[1].split('"')[0]
                    phone = item.split('"contactNumber":"')[1].split('"')[0]
                    state = item.split('"province":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(',')[0]
                    lng = item.split('"longitude":')[1].split(',')[0]
                    r2 = session.get(loc, headers=headers)
                    hours = ''
                    dc = 0
                    for line2 in r2.iter_lines():
                        line2 = str(line2.decode('utf-8'))
                        if '<span class="C_DD-display">' in line2:
                            day = line2.split('<span class="C_DD-display">')[1].split('<')[0]
                        if 'data-opening-hours="' in line2:
                            hrs = day + ': ' + line2.split('data-opening-hours="')[1].split('"')[0]
                            if dc <= 6:
                                if hours == '' and 'Sun.' not in hours:
                                    hours = hrs
                                    dc = dc + 1
                                else:
                                    dc = dc + 1
                                    hours = hours + '; ' + hrs
                    typ = 'Dealer'
                    if hours == '':
                        hours = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
