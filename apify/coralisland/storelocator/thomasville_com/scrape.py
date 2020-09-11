import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.thomasvillecabinetry.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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
            state = addr[0].replace(',', '') + ' '
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }


def fetch_data():
    session = requests.Session()
    history = []
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json',
            'Cookie': 'Authsite=httpss%3A%2F%2Fwww.thomasvillecabinetry.com%2Fstore-locator; AppKey=NONE; W2GISM=980e5389824791d83872e25a7ff1444e',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        for city in city_list:
            url = 'https://hosted.where2getit.com/thomasville/rest/locatorsearch?like=0.8373297688405197&lang=en_US'
            payload = {
                "request":{ 
                    "appkey":"D1A3CDF0-E43F-11E7-977E-87C8F48ECC77",
                    "formdata":{
                        "geoip":"false",
                        "order":"_DISTANCE",
                        "dataview":"store_default",
                        "limit":10000,
                        "atleast":2,
                        "geolocs":{
                            "geoloc":[
                                {
                                    "addressline":city['city'],
                                    "country":"US",
                                    "latitude":"",
                                    "longitude":""
                                }
                            ]
                        },
                        "searchradius":"200",
                        "where":{
                            "or":{
                                "classic":{
                                    "eq":""
                                },
                                "studio_1904":{
                                    "eq":""
                                },
                                "nouveau":{
                                    "eq":""
                                },
                                "artisan":{
                                    "eq":""
                                }
                            }
                        },
                        "false":"0"
                    }   
                }
            }
            request = session.get(url, headers=headers, data=json.dumps(payload))        
            store_list = json.loads(request.text)['response']
            if 'collection' in store_list:
                store_list = store_list['collection']
                for store in store_list:                    
                    store_id = get_value(store.get('uid')).replace('-', '')
                    uni_key = store_id + validate(store.get('latitude')) + validate(store.get('longitude'))
                    if uni_key not in history:
                        history.append(uni_key)
                        output = []
                        output.append(base_url) # url
                        output.append('https://www.cat.com/en_US.html') # page url
                        output.append(get_value(store.get('name'))) #location name
                        output.append(get_value(store.get('address1'))) #address
                        output.append(get_value(store.get('city'))) #city
                        output.append(get_value(store.get('state'))) #state
                        output.append(get_value(store.get('postalcode'))) #zipcode
                        output.append(get_value(store.get('country'))) #country code
                        output.append(get_value(store_id)) #store_number
                        output.append(get_value(store.get('phone'))) #phone
                        output.append('Thomasville Cabinetry') #location type
                        output.append(get_value(store.get('latitude'))) #latitude
                        output.append(get_value(store.get('longitude'))) #longitude
                        store_hours = []
                        output.append(get_value(store_hours)) #opening hours
                        writer.writerow(output)
                    
fetch_data()
