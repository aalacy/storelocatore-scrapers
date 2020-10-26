import csv
import re
import pdb
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


base_url = 'https://fasteddiesbilliards.com'

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
        if item != '' and item != '|':
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
        writer.writerow(["locator_domain",'page_url', "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://fasteddiesbilliards.com"
    #session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@id="locations"]//a/@href')
    for store_link in store_list[:-1]:
        #print(store_link)
        if store_link.find('round-rock') > -1:
            store_link = 'https://fasteddiesbilliards.com/round-rock-tx'
        store = etree.HTML(session.get(store_link,headers=headers).text)
        detail = eliminate_space(store.xpath('.//div[@id="info"]//div[@class="wpb_text_column wpb_content_element "]//text()'))
        output = []
        output.append(base_url) # url
        output.append(store_link)
        address = detail[-1].split('|')
        output.append(address[1].split(',')[0].replace('\xa0','').lstrip()) #location name
        output.append(address[0].replace('\xa0','').lstrip()) #address
        output.append(address[1].split(',')[0].replace('\xa0','').lstrip()) #city
        output.append(address[1].split(',')[1].replace('\xa0','').lstrip()) #state
        output.append('<MISSING>') #zipcode   
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(detail[-2]) #phone
        output.append("Fast Eddie's Billiards | Sports Tavern & Social Club") #location type
        geo_loc = validate(store.xpath('.//div[@class="col span_12  left"]//a[contains(@class, "nectar-button")]/@href')[0]).split('/@')
        if len(geo_loc) > 1:
            geo_loc = geo_loc[1].split(',17z')[0].split(',')
            output.append(geo_loc[0]) #latitude
            output.append(geo_loc[1]) #longitude
        else:
            geo_loc = validate(store.xpath('.//div[@id="info"]//div[@class="wpb_text_column wpb_content_element "]//a/@href')[1]).split('/@')
            try:
                geo_loc = geo_loc[1].split(',17z')[0].split(',')
                output.append(geo_loc[0]) #latitude
                output.append(geo_loc[1]) #longitude
            except:
                output.append('<INACCESSIBLE>') #latitude
                output.append('<INACCESSIBLE>') #longitude
        store_hours = validate(detail[:-2]).replace('18 years old and up, ', '').replace('|', '')
        output.append(get_value(store_hours)) #opening hours
        #print(output)
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
