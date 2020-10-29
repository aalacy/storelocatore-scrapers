import csv
import re
import pdb
from lxml import etree
import json

from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thegreatmaple_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

base_url = 'https://thegreatmaple.com'

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain",'page_url', "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://thegreatmaple.com/"
    #session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//li[@id="menu-item-15359"]')[0].xpath('.//a/@href')[1:]

    for store_link in store_list:
        #logger.info(store_link)
	
        store = etree.HTML(session.get(store_link, headers=headers).text)
        try:
           details = eliminate_space(store.xpath('.//div[@class="tatsu-text-inner tatsu-align-center  clearfix"]')[0].xpath('.//text()'))
           
        except:
           store = etree.HTML(session.get(store_link, headers=headers).text)

           details = eliminate_space(store.xpath('.//div[@class="tatsu-text-inner tatsu-align-center  clearfix"]')[0].xpath('.//text()'))
        
        if store_link =='http://thegreatmaple.com/sandiego':
            details = eliminate_space(store.xpath('.//div[@class="tatsu-text-inner tatsu-align-center  clearfix"]')[1].xpath('.//text()'))
        point = 0
        #logger.info(details)
        for idx, de in enumerate(details):
            if 'hours' == de.lower():
                point = idx
                break
        output = []        
        output.append(base_url)
        output.append(store_link)# url
        if details[point-4].lower() != 'address':
            output.append(details[point-4]) #location name
        else:
            output.append('<MISSING>') #location name
        #logger.info(details[point-3])
        output.append(details[point-3]) #address
        address = details[point-2].strip().split(',')
#        logger.info(address)
        output.append(address[0]) #city
        output.append(address[1].strip().split(' ')[0]) #state
        output.append(address[1].strip().split(' ')[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(details[point-1]) #phone
        output.append("Great Maple | A Modern American Eatery") #location type
        output.append(validate(store.xpath('.//div[contains(@class, "tatsu-gmap map_")]/@data-latitude'))) #latitude
        output.append(validate(store.xpath('.//div[contains(@class, "tatsu-gmap map_")]/@data-longitude'))) #longitude
        hours = validate(details[point+1:]).replace('•','')
        try:
            hours = hours.split('HOURS')[0]
        except:
            pass
        try:
            hours = hours.split('Happy')[0]
        except:
            pass
        try:
            hours = hours.split('Check')[0]
        except:
            pass
        
        output.append(hours) #opening hours
       # logger.info(output)
        output_list.append(output)        
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
