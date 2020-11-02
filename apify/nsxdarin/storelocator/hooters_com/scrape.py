import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sgzip import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hooters_com')



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
    ids = []
    for code in sgzip.for_radius(50):
        logger.info(('Pulling Postal Code %s...' % code))
        url = 'https://www.hooters.com/api/search_locations.json?address=' + code
        r2 = session.get(url, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line in r2.iter_lines(decode_unicode=True):
            if '"id":"' in line:
                items = line.split('"id":"')
                for item in items:
                    if '"cost_center":"' in item and 'Mexico' not in item:
                        store = item.split('"')[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        try:
                            phone = item.split(',"phone":"')[1].split('"')[0]
                        except:
                            phone = '<MISSING>'
                        website = 'hooters.com'
                        typ = '<MISSING>'
                        try:
                            zc = item.split('"zip":"')[1].split('"')[0]
                        except:
                            zc = '<MISSING>'
                        add = item.split('"line-1":"')[1].split('"')[0]
                        city = item.split('"line-2":"')[1].split(',')[0]
                        state = item.split('"line-2":"')[1].split(',')[1].strip().split(' ')[0]
                        country = 'US'
                        lat = item.split('"latitude":"')[1].split('"')[0]
                        lng = item.split('"longitude":"')[1].split('"')[0]
                        loc = 'https://www.hooters.com/locations/' + item.split('"slug":"')[1].split('"')[0]
                        try:
                            hours = 'Mon: ' + item.split('"mon"')[1].split('"open":"')[1].split(':00"')[0] + '-' + item.split('"mon":{')[1].split('"close":"')[1].split(':00"')[0]
                            hours = hours + '; Tue: ' + item.split('"tue"')[1].split('"open":"')[1].split(':00"')[0] + '-' + item.split('"tue":{')[1].split('"close":"')[1].split(':00"')[0]
                            hours = hours + '; Wed: ' + item.split('"wed"')[1].split('"open":"')[1].split(':00"')[0] + '-' + item.split('"wed":{')[1].split('"close":"')[1].split(':00"')[0]
                            hours = hours + '; Thu: ' + item.split('"thu"')[1].split('"open":"')[1].split(':00"')[0] + '-' + item.split('"thu":{')[1].split('"close":"')[1].split(':00"')[0]
                            hours = hours + '; Fri: ' + item.split('"fri"')[1].split('"open":"')[1].split(':00"')[0] + '-' + item.split('"fri":{')[1].split('"close":"')[1].split(':00"')[0]
                            hours = hours + '; Sat: ' + item.split('"sat"')[1].split('"open":"')[1].split(':00"')[0] + '-' + item.split('"sat":{')[1].split('"close":"')[1].split(':00"')[0]
                            hours = hours + '; Sun: ' + item.split('"sun"')[1].split('"open":"')[1].split(':00"')[0] + '-' + item.split('"sun":{')[1].split('"close":"')[1].split(':00"')[0]
                        except:
                            hours = '<MISSING>'
                        if store not in ids:
                            ids.append(store)
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
