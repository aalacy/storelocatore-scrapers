import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('penn__station_com')




base_url = 'https://www.penn-station.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
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

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '')
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    history = []
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)
    output_list = []
    url = "https://www.penn-station.com/storefinder_responsive/index.php"
    session = requests.Session()
    headers = {
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': '__cfduid=d8bd814a58dc6c014bf8914928e3a92291566153613; _omappvp=nJQFJFnhsPJJRioTHkJAJKCdSpquw9EanP31LYWCzRCqv3byAhceKkU2DcpaiDsFr4AZRICJdtkESa2J5g4I4m3bkXgHs3FD; PHPSESSID=fc63eddd1c7dc180e37a8f256d111ee2',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    for city in city_list:
        data = {
            'ajax': '1',
            'action': 'get_nearby_stores',
            'distance': '1000',
            'lat': str(city['latitude']),
            'lng': str(city['longitude']),
            'products': '1'
        }
        request = session.post(url, data=data, headers=headers)
        data = json.loads(validate(request.text))
        if 'stores' in data:
            store_list = data['stores']
            logger.info(city)
            for store in store_list:
                output = []
                uni = get_value(store['name'] + store['address'])
                if uni not in history:
                    output.append(base_url) # url
                    output.append(get_value(store['name'])) #location name
                    address = parse_address(get_value(store['address']))
                    output.append(address['street']) #address
                    output.append(address['city']) #city
                    output.append(address['state']) #state
                    output.append(address['zipcode']) #zipcode
                    output.append('US') #country code
                    output.append('<MISSING>') #store_number
                    output.append(get_value(store['telephone'])) #phone
                    output.append("Super Store Finder") #location type
                    output.append(get_value(store['lat'])) #latitude
                    output.append(get_value(store['lng'])) #longitude
                    output.append(get_value(store['description']).replace(';', ', ')) #opening hours
                    output_list.append(output)
                    history.append(uni)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
