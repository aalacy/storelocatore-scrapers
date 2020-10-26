import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
import usaddress
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('omahasteaks_com')



base_url = 'https://www.omahasteaks.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace(u'\u2013', '-').replace('\n', '').replace('\t', '').strip()

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
    output_list = []
    url = "https://www.omahasteaks.com/info/Stores-Locations"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//a[@class="citylink"]/@href')
    for store_link in store_list:
        logger.info(store_link)
        store = etree.HTML(session.get(store_link, headers=headers).text)
        details = eliminate_space(store.xpath('.//div[@style="line-height: 120%"]//text()'))
        address = ''
        phone = ''
        store_hours = ''
        for idx, de in enumerate(details):
            if 'phone' in de.lower():
                phone = validate(de.replace('Phone:', ''))
                address = ', '.join(details[idx-2:idx])
            if 'hours:' in de.lower():
                store_hours = validate(details[idx+1:])
        output = []
        output.append(base_url) # url
        output.append(store_link) # page_url
        output.append(validate(store.xpath('.//b[@class="body14"]')[0].xpath('.//text()'))) #location name
        address = parse_address(address)
        output.append(address['street']) #address
        city = address['city']
        output.append(city) #city
        output.append(address['state']) #state
        output.append(address['zipcode']) #zipcode
        output.append('US') #country code
        output.append(re.findall(r'storeid=[0-9]{1,10}', store_link)[0].split("=")[-1]) #store_number
        output.append(get_value(phone)) #phone
        output.append("<MISSING>") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        if not store_hours:
            store_hours = store.xpath('.//div[@class="border"]/b')[0].text.replace("Almost all stores are now operating","").strip()
            store_str = str(store.xpath('.//div[@class="border"]/text()'))
            if city == "South Windsor" and "South Windsor, CT is open" in store_str:
                store_hours = re.findall(r'South Windsor, CT .+ Sunday', store_str)[0].replace("South Windsor, CT is open","")
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
