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
    with open('./US_CA_States.json') as data_file:    
        state_list = json.load(data_file)
    url = "https://www.scheels.com/on/demandware.store/Sites-scheels-Site/en_US/Stores-FindStores?format=ajax"
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': '__cfduid=db112c423382dcb102cd3a330ecdc46e41568761790; dwanonymous_16c62f0fb62b4e9ca8c672ae8f1aebcf=bdZW71l80WEcg2trmpkbfaZPZ5; emailPopUp=true; dwsid=bJA4QAvIy0mYdjJmDwyW38xo2EabsZ8bYhdckvEPdCniIuH3Oe4EQy3OGqsfs2ET9KFFb95fVR3x4K-SkaJE6g==; dwac_0bf042884e2e2eccd8c2a0151d=8X5YfG4CSYRq6Yj22V5B2VGGuHr-ex3WkIg%3D|dw-only|||USD|false|US%2FCentral|true; cqcid=bdZW71l80WEcg2trmpkbfaZPZ5; sid=8X5YfG4CSYRq6Yj22V5B2VGGuHr-ex3WkIg; dwsecuretoken_16c62f0fb62b4e9ca8c672ae8f1aebcf=rqXP4KNP1vyYFY4uKvEnQ_0dKwNoL2AEhw==; __cq_dnt=0; dw_dnt=0; dw=1; dw_cookies_accepted=1; TT3bl=false; TURNTO_VISITOR_SESSION=1; TURNTO_VISITOR_COOKIE=S0GBG7nfqhwViwa,1,0,0,null,,,0,0,0,0,0,0,0; TURNTO_TEASER_SHOWN=1573559613327',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for state in state_list:
            session = requests.Session()
            formdata = {
                'dwfrm_storelocator_searchterm': state['abbreviation'],
                'dwfrm_storelocator_maxdistance': '999999',
            }
            request = session.post(url, headers=headers, data=formdata)
            store_list = etree.HTML(request.text).xpath('.//li')
            for store in store_list:
                store_id = get_value(store.xpath('.//a[contains(@class, "store-details-link")]/@id'))
                if store_id not in history:
                    history.append(store_id)
                    store_link = base_url + validate(store.xpath('.//a[contains(@class, "store-details-link")]/@href'))
                    output = []
                    output.append(base_url) # url
                    output.append(store_link) # page url
                    output.append(get_value(store.xpath('.//span[contains(@class, "store-name")]//text()'))) #location name
                    output.append(get_value(store.xpath('.//span[contains(@class, "address1")]//text()'))) #address
                    output.append(get_value(store.xpath('.//span[contains(@class, "city")]//text()'))) #city
                    output.append(get_value(store.xpath('.//span[contains(@class, "state")]//text()'))) #state
                    output.append(get_value(store.xpath('.//span[contains(@class, "postal-code")]//text()'))) #zipcode
                    output.append('US') #country code
                    output.append(store_id) #store_number
                    output.append(get_value(store.xpath('.//div[contains(@class, "store-phone")]//text()'))) #phone
                    output.append('Scheels Store') #location type
                    output.append(get_value(store.xpath('.//span[contains(@class, "latitude")]//text()'))) #latitude
                    output.append(get_value(store.xpath('.//span[contains(@class, "longitude")]//text()'))) #longitude
                    store_hours = eliminate_space(etree.HTML(session.get(store_link).text).xpath('.//div[@class="cell store-hours"]//p//text()'))
                    if len(store_hours) != 0:
                        output.append(get_value(store_hours)) #opening hours
                        writer.writerow(output)
            
fetch_data()