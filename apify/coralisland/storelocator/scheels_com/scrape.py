import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.scheels.com'

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
    output_list = []
    with open('states.json') as data_file:    
        state_list = json.load(data_file)
    session = requests.Session()
    url = "https://www.scheels.com/on/demandware.store/Sites-scheels-Site/en_US/Stores-FindStores?format=ajax"
    for state in state_list:
        headers = {
            'accept': '*/*',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'cookie': '__cfduid=db112c423382dcb102cd3a330ecdc46e41568761790; dwanonymous_16c62f0fb62b4e9ca8c672ae8f1aebcf=bdZW71l80WEcg2trmpkbfaZPZ5; emailPopUp=true; dwsid=EWslPTGE5cfovPA7wKOfUbsXwU8N4_7-pDgILnJcD7cIUvc-JAPM-YafXaKSNILt-y0Q8-moWp9VqE_-5pKHeg==; dwac_0bf042884e2e2eccd8c2a0151d=myVqR89aEeAWoglxJ0cumzFZjjXzPQrZWiY%3D|dw-only|||USD|false|US%2FCentral|true; cqcid=bdZW71l80WEcg2trmpkbfaZPZ5; sid=myVqR89aEeAWoglxJ0cumzFZjjXzPQrZWiY; dwsecuretoken_16c62f0fb62b4e9ca8c672ae8f1aebcf=t_Ngx1fhhuUAKRMyiwn-XnoafM7rHVhhCw==; __cq_dnt=0; dw_dnt=0; dw=1; dw_cookies_accepted=1; TT3bl=false; TURNTO_VISITOR_SESSION=1; TURNTO_VISITOR_COOKIE=xZaG4PTauxBRxVT,1,0,0,null,,,0,0,0,0,0,0,0; TURNTO_TEASER_SHOWN=1569015761111',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        formdata = {
            'dwfrm_storelocator_searchterm': state['abbreviation'],
            'dwfrm_storelocator_maxdistance': '999999'
        }
        source = session.post(url, headers=headers, data=formdata).text
        response = etree.HTML(source)
        store_list = response.xpath('.//div[@id="store-location-results"]//li')
        for store in store_list:
            store_link = base_url + validate(store.xpath('.//a[contains(@class, "store-details-link")]/@href'))
            number = validate(store.xpath('.//a[contains(@class, "store-details-link")]/@id'))
            lat = validate(store.xpath('.//span[contains(@class, "latitude")]//text()'))
            lng = validate(store.xpath('.//span[contains(@class, "longitude ")]//text()'))
            store = etree.HTML(session.get(store_link).text)
            output = []
            output.append(base_url) # url
            output.append(validate(store.xpath('.//div[@id="store-main-contact"]//h1//text()'))) #location name
            address = validate(store.xpath('.//div[@class="cell store-address"]//p//text()'))
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
            output.append('US') #country code
            output.append(get_value(number)) #store_number
            output.append(get_value(store.xpath('.//div[@class="cell store-phone"]//p//text()'))) #phone
            output.append("Sandy Scheels") #location type
            output.append(get_value(lat)) #latitude
            output.append(get_value(lng)) #longitude
            store_hours = get_value(store.xpath('.//div[@class="cell store-hours"]//p//text()'))
            output.append(get_value(store.xpath('.//div[@class="cell store-hours"]//p//text()'))) #opening hours
            if store_hours != '<MISSING>':
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
