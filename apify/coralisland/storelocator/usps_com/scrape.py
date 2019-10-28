import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.usps.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').encode('ascii', 'ignore').encode("utf8").strip()

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
    output_list = []
    history = []
    with open('cities.json') as data_file:    
        city_list = json.load(data_file)  
    url = "https://tools.usps.com/UspsToolsRestServices/rest/POLocator/findLocations"
    headers = {       
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'content-type': 'application/json;charset=UTF-8',
        'cookie': 'JSESSIONID=0000JrtkaUwPFvf2Pmw8Bgmttdf:1bbcn20cc; NSC_uppmt-xbt8-mc=ffffffff3b22378945525d5f4f58455e445a4a4212d3; NSC_tibqf-ipq1-mc_443=ffffffff3b461d1545525d5f4f58455e445a4a42378b',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    page_url = 'https://tools.usps.com/find-location.htm'
    session = requests.Session()
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for city in city_list:
            payload = {
                "maxDistance": "100",
                "requestCity": city['city'],
                "requestRefineHours": "",
                "requestRefineTypes": "",
                "requestServices": "",
                "requestState": city['state'],
                "requestType": "po"
            }
            request = session.post(url, headers=headers, data=json.dumps(payload))
            store_list = json.loads(request.text)['locations']        
            for store in store_list:
                if get_value(store['locationID']) not in history:                
                    history.append(get_value(store['locationID']))
                    output = []
                    output.append(base_url) # url
                    output.append(page_url) # page url
                    output.append(get_value(store['locationName'])) #location name
                    output.append(get_value(store['address1'])) #address
                    output.append(get_value(store['city'])) #city
                    output.append(get_value(store['state'])) #state
                    zipcode = store['zip5']
                    if 'zip4' in store:
                        zipcode += '-' + store['zip4']
                    output.append(get_value(zipcode)) #zipcode
                    output.append('US') #country code
                    output.append(get_value(store['locationID'])) #store_number
                    output.append(get_value(store['phone'])) #phone
                    output.append('Usps') #location type
                    output.append(get_value(store['latitude'])) #latitude
                    output.append(get_value(store['longitude'])) #longitude
                    store_hours = []
                    if len(store['locationServiceHours']) > 0:
                        for hour in store['locationServiceHours'][0]['dailyHoursList']:
                            if len(hour['times']) > 0:
                                duration = validate(hour['times'][0]['open']) + '-' + validate(hour['times'][0]['close'])
                            else:
                                duration = 'closed'
                            store_hours.append(validate(hour['dayOfTheWeek'] + ' ' + duration))            
                    output.append(get_value(store_hours)) #opening hours
                    # output_list.append(output)  
                    writer.writerow(output)


fetch_data()

