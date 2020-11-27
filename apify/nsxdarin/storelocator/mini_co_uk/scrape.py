import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

logger = SgLogSetup().get_logger('mini_co_uk')

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://c2b-services.bmw.com/c2b-localsearch/services/api/v4/clients/BMWSTAGE2_DLO/UK/pois?brand=MINI&cached=off&callback=angular.callbacks._0&category=MI&country=GB&language=en&lat=0&lng=0&maxResults=700&showAll=true&unit=km'
    r = session.get(url, headers=headers)
    website = 'mini.co.uk'
    typ = '<MISSING>'
    country = 'GB'
    hours = '<MISSING>'
    logger.info('Pulling Stores')
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '{"key":"' in line:
            items = line.split('{"key":"')
            for item in items:
                if '"countryCode":"' in item:
                    name = item.split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    add = item.split('"street":"')[1].split('"')[0]
                    try:
                        add = add + ' ' + item.split('"additionalStreet":"')[1].split('"')[0]
                    except:
                        pass
                    city = item.split('"city":"')[1].split('"')[0]
                    lat = item.split('"lat":')[1].split(',')[0]
                    lng = item.split('"lng":')[1].split(',')[0]
                    try:
                        state = item.split('"state":"')[1].split('"')[0]
                    except:
                        state = '<MISSING>'
                    loc = '<MISSING>'
                    phone = item.split('"phone":"')[1].split('"')[0]
                    store = item.split('"')[0]
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
