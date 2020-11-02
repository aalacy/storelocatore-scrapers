import csv
from sgrequests import SgRequests
from io import StringIO
from html.parser import HTMLParser
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('prairielife_com')



class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

base_url = 'https://prairielife.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    while True:
        if item[-1:] == ' ':
            item = item[:-1]
        else:
            break
    return item.strip()

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'referer': 'https://www.genesishealthclubs.com/locations',
    'host': 'www.genesishealthclubs.com'
}

def fetch_data():
    session = SgRequests()
    url = "https://www.genesishealthclubs.com/geoClub.php?getClubData=1&club_id={}"
    store_id = 1
    misses = 0
    while True:
        store_endpoint = url.format(store_id)
        data = session.get(store_endpoint, headers=headers).json()
        if 'path' not in data:
            logger.info(store_id)
            if misses >= 100:
                break
            else:
                misses += 1
                store_id += 1
                continue
        else:
            misses = 0
        locator_domain = 'genesishealthclubs.com'
        location_name = get_value(data['name'])
        street_address = get_value(data['address'])
        city = get_value(data['city'])
        state = get_value(data['state'])
        zipcode = get_value(data['zip_code'])
        country_code = 'US'
        store_number = data['id']
        phone = get_value(data['phone'])
        location_type = '<MISSING>'
        latitude = get_value(data['latitude'])
        longitude = get_value(data['longitude'])
        hours_of_operation = ', '.join([strip_tags(x) for x in data['hours'].replace('</div><div', '</div>\n<div').splitlines()])
        page_url = 'https://www.genesishealthclubs.com/locations/{}.html'.format(data['path'])
        store_id += 1
        yield [locator_domain, location_name, street_address, city, state, zipcode, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
