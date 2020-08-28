from sgrequests import SgRequests
import csv
import sgzip
from lxml import (html, etree,)
import re
import json
from tenacity import *

LIST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
    ,'Accept-Encoding': 'gzip, deflate, br'
    ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
    ,'Connection': 'keep-alive'
    ,'Host': 'mstores.barnesandnoble.com'
    ,'Referer': 'https://mstores.barnesandnoble.com/stores'
    ,'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1'
}

STORE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Referer": "https://stores.barnesandnoble.com/stores?searchText=94107&view=list&storeFilter=all",
    "Host": "stores.barnesandnoble.com",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}

URL = 'https://mstores.barnesandnoble.com/stores'

session = SgRequests() 

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['us', 'ca'])

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    return field

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def xpath(hxt, query_string):
    hxp = hxt.xpath(query_string)
    if hxp:
        if hasattr(hxp[0], 'encode'):
            return hxp[0].encode('ascii', 'ignore')
        return hxp[0]
    return None

def get_store_id(location):
    store_id = str(xpath(location, './/a/@href'))
    store_id = re.findall(r'[0-9]+', store_id)
    store_id = store_id[0] if store_id else None
    return store_id

def crawl_zip_code(code):
    query_params = {
        'page': None
        ,'size': 100
        ,'searchText': code
        ,'storeFilter': 'all'
       ,'view': 'list'
        ,'v': 1
    }
    request = session.get(URL, params=query_params, headers=LIST_HEADERS)
    hxt = html.fromstring(request.text)
    locations = hxt.xpath('//div[@class="col-sm-12 col-md-8 col-lg-8 col-xs-12"]')
    for location in locations:
        store_id = get_store_id(location)
        yield store_id

def fetch_store_ids():
    store_ids = set()
    zip_code = search.next_zip()
    while zip_code:
        print('{} zip codes remaining'.format(search.zipcodes_remaining()))
        new_ids = crawl_zip_code(zip_code)
        store_ids.update(new_ids)
        search.max_distance_update(50.0)
        zip_code = search.next_zip()
    return store_ids

def parse_store(store):
    locator_domain = 'bn.com'
    page_url = 'https://stores.barnesandnoble.com/store/{}'.format(store['storeId'])
    location_name = handle_missing(store['name'])
    street_address = handle_missing(store['address2'] if 'address2' in store else store['address1'])
    city = handle_missing(store['city'])
    state = handle_missing(store['state'])
    zip_code = handle_missing(store['zip'])
    country_code = '<MISSING>'
    store_number = handle_missing(store['storeId'])
    phone = handle_missing(store['phone'])
    location_type = '<MISSING>'
    latitude = handle_missing(store['location'][1])
    longitude = handle_missing(store['location'][0])
    hours_of_operation = handle_missing(store['hours'])
    return [locator_domain, page_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation]

@retry(stop=stop_after_attempt(3))
def fetch_store(store_id):
    global session
    response = session.get('https://stores.barnesandnoble.com/direction/store/{}'.format(store_id), headers=STORE_HEADERS)
    for line in (str(x) for x in response.iter_lines()):
        if 'var storesJson' in line:
            store_json = line[line.index('['):len(line) - line[::-1].index(']')].encode('latin1').decode('unicode-escape')
            store = json.loads(store_json)[0]
            return parse_store(store)
    print(response.text)
    session = SgRequests()
    raise Exception("Store json not found for id {}".format(store_id))

def fetch_stores(store_ids):
    for store_id in store_ids:
        store = None
        try:
            store = fetch_store(store_id)
        except:
            print("store id failed: {}".format(store_id))
            raise
        yield store

def fetch_data():
    store_ids = fetch_store_ids()
    return fetch_stores(store_ids)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
