import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
import usaddress


base_url = 'https://www.mirabito.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').strip()

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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()
    output_list = []
    url = "https://www.mirabito.com/locations/"
    source = session.get(url).text
    data = source.split('var maplistScriptParamsKo = ')[1].split('};')[0] + '}'
    store_list = json.loads(data)['KOObject'][0]['locations']
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(url) # page_url
        output.append(get_value(store['title'])) #location name
        details = eliminate_space(etree.HTML(store['description']).xpath('.//text()'))
        address = ''
        store_hours = ''
        phone = ''
        for idx, de in enumerate(details):
            if 'hours' in de.lower():
                address = validate(details[:idx])
                store_hours = de.replace('Store Hours:', '')
            if 'phone' in de.lower():
                phone = details[idx+1]
        address = parse_address(address.replace('Tim Hortons is full service.', ''))
        if address['street'] == '<MISSING>':
            details = eliminate_space(etree.HTML(store['address']).xpath('.//text()'))
            address = []
            for de in details:
                if '-' not in de:
                    address.append(de)

            address = parse_address(validate(address))
        street = address['street']
        if street == "16 Business Blvd.":
            city = "Castleton-On-Hudson"
            state = "NY"
            zipcode = "12033"
        else:
            city = address['city']
            state = address['state']
            zipcode = address['zipcode']
            if street == "8536 Seneca Turnpike":
                zipcode = "13413"
            if street == "54 Elm St.":
                zipcode = "13753"            
        output.append(street) #address
        output.append(city) #city
        output.append(state) #state
        output.append(zipcode) #zipcode
        output.append('US') #country code
        store_number = store['title'].split("#")[-1]
        if not store_number.isnumeric():
            store_number = '<MISSING>'
        output.append(store_number) #store_number
        output.append(get_value(phone)) #phone
        output.append('<MISSING>') #location type
        output.append(get_value(store['latitude'])) #latitude
        output.append(get_value(store['longitude'])) #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
