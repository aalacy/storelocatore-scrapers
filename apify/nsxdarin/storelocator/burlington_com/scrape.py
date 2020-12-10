import csv
from sgrequests import SgRequests
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('burlington_com')

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
    ids = []
    for code in sgzip.for_radius(200):
        logger.info('Pulling Zip Code %s...' % code)
        url = 'https://www.mapquestapi.com/search/v2/radius?key=kY8VAT7oi6AlAXPCq0XNQsuvjV2Cx4Wb&callback=jQuery19206669057244423291_1605555135749&origin=' + code + '+US&radius=200&hostedData=mqap.kY8VAT7oi6AlAXPCq0XNQsuvjV2Cx4Wb_bcf_stores&_=1605555135750'
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            items = line.split('{"distanceUnit":"')
            for item in items:
                if '"distance":' in item:
                    store = item.split('"name":"')[1].split('"')[0]
                    name = 'Burlington Store #' + store
                    phone = item.split('"phone":"')[1].split('"')[0][:14]
                    add = item.split(',"address":"')[1].split('"')[0]
                    lat = item.split(',"Lat":')[1].split('}')[0]
                    lng = item.split('{"lng":')[1].split(',')[0]
                    website = 'burlington.com'
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"postal":"')[1].split('"')[0]
                    country = 'US'
                    typ = 'Store'
                    hours = item.split('"hours1":"')[1].split('"')[0]
                    hours = hours + ' ' + item.split('"hours2":"')[1].split('"')[0]
                    hours = hours + ' ' + item.split('"hours3":"')[1].split('"')[0]
                    hours = hours.strip()
                    if store not in ids:
                        ids.append(store)
                        if 'Opening' not in hours:
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
