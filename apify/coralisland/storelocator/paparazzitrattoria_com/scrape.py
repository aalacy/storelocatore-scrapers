import csv
import re
import pdb
from lxml import etree
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('paparazzitrattoria_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


base_url = 'https://www.paparazzitrattoria.com'

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.paparazzitrattoria.com"
    #session = requests.Session()    
    request = session.get(url, headers=headers, verify=False)   
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="location"]')
    logger.info(len(store_list))
    for store in store_list:
        link = validate(store.xpath('./a/@href'))
        store = eliminate_space(store.xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(link)
        output.append(store[0]) #location name
        output.append(store[1]) #address
        address = store[2].strip().split(',')
        output.append(address[0]) #city
        output.append(eliminate_space(address[1].strip().split(' '))[0]) #state
        output.append(eliminate_space(address[1].strip().split(' '))[1]) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[3]) #phone
        output.append("Papa Razzi | Italian Scratch Cooking") #location type
        source = session.get(link, headers=headers)
        detail = source.text
        geolocation = detail.split('LatLng(')[1].split(')')[0]
        lat,longt = geolocation.split(', ')
        output.append(lat)
        output.append(longt)
        #store_hours = ' '.join(eliminate_space(detail.xpath('.//div[@id="hours"]//p//text()')))
         #opening hours
        output.append('<INACCESSIBLE>')
        #logger.info(output)
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
