import csv
import re
import pdb
import requests
from lxml import etree
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mauiwowi_com')



base_url = 'http://www.mauiwowi.com'

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "http://www.mauiwowi.com/Locations"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="divLocationListItem clearfix"]//a/@href')
    for link in store_list:
        logger.info(link)
        link = base_url + '/' + link        
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//div[@class="divContainer divContainerStandard divContainer215 clearfix"]//h3//text()'))) #location name
        output.append(get_value(store.xpath('.//div[@class="divContainer divContainerStandard divContainer215 clearfix"]//span[@itemprop="streetAddress"]//text()'))) #address        
        output.append(get_value(store.xpath('.//div[@class="divContainer divContainerStandard divContainer215 clearfix"]//span[@itemprop="addressLocality"]//text()'))) #city
        output.append(get_value(store.xpath('.//div[@class="divContainer divContainerStandard divContainer215 clearfix"]//span[@itemprop="addressRegion"]//text()'))) #state
        output.append(get_value(store.xpath('.//div[@class="divContainer divContainerStandard divContainer215 clearfix"]//span[@itemprop="postalCode"]//text()'))) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@class="divContainer divContainerStandard divContainer215 clearfix"]//span[@itemprop="telephone"]//text()'))) #phone
        output.append("Maui Wowi Hawaiian Coffees & Smoothies") #location type
        output.append("<INACCESSIBLE>") #latitude
        output.append("<INACCESSIBLE>") #longitude
        store_hours = store.xpath('.//div[@class="divContainer divContainerStandard divContainer215 clearfix"]//table[@class="tableListHours"]//tr')
        h_temp = []
        for hour in store_hours:
            h_temp.append(validate(eliminate_space(hour.xpath('.//text()'))))
        output.append(', '.join(h_temp)) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
