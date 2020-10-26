import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('coldstonecreamery_com')



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
    url = 'https://www.coldstonecreamery.com/locator/index.php?brand=14&mode=desktop&pagesize=7000&q=55441&latitude=&longitude='
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'Locator.stores[' in line:
            store = line.split('"StoreId":')[1].split(',')[0]
            logger.info(('Pulling Store %s...' % store))
            website = 'coldstonecreamery.com'
            name = 'Cold Stone #' + store
            lat = line.split('"Latitude":')[1].split(',')[0]
            lng = line.split('"Longitude":')[1].split(',')[0]
            add = line.split('"Address":"')[1].split('"')[0]
            city = line.split('"City":"')[1].split('"')[0]
            state = line.split('"State":"')[1].split('"')[0]
            zc = line.split('"Zip":"')[1].split('"')[0]
            country = line.split('"CountryCode":"')[1].split('"')[0]
            phone = line.split('"Phone":"')[1].split('"')[0]
            typ = 'Restaurant'
            surl = 'https://www.coldstonecreamery.com/stores/' + store
            r2 = session.get(surl, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            lines = r2.iter_lines(decode_unicode=True)
            for line2 in lines:
                if '<ul class="hours">' in line2:
                    g = next(lines)
                    hours = g.replace('</li><li>','; ').replace('<li>','').replace('</li>','').strip().replace('\r','').replace('\t','').replace('\n','')
            if 'lease contact' in hours:
                hours = '<MISSING>'
            if phone == '' or phone == '() -':
                phone = '<MISSING>'
            if country == 'US' or country == 'CA':
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
