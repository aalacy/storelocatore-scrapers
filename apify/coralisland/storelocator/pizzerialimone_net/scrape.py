import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.pizzerialimone.net'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

def get_value(item):
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
    url = "https://www.pizzerialimone.com/locations"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//section[@class="Main-content"]//div[@class="row sqs-row"][1]//div[@class="sqs-block-content"]//p')
    title_list = response.xpath('//section[@class="Main-content"]//div[@class="row sqs-row"][1]//div[@class="sqs-block-content"]//h2')
    store_hours = validate(response.xpath('//section[@class="Main-content"]//div[@class="row sqs-row"][2]//div[@class="sqs-block-content"]')[0].xpath('.//text()')).replace('All locations Open ', '')
    for idx, store in enumerate(store_list):
        store = eliminate_space(store.xpath('.//text()'))
        title = validate(title_list[idx].xpath('.//text()'))
        output = []
        output.append(base_url) # url
        output.append(title) #location name
        address = ', '.join(store[:-1])
        address = usaddress.parse(address)
        street = ''
        city = ''
        state = ''
        zipcode = ''
        for addr in address:
            if addr[1] == 'PlaceName':
                city += addr[0].replace(',', '') + ' '
            elif addr[1] == 'ZipCode':
                zipcode = addr[0]
            elif addr[1] == 'StateName':
                state = addr[0]
            else:
                street += addr[0].replace(',', '') + ' '
        output.append(get_value(street)) #address
        output.append(get_value(city)) #city
        output.append(get_value(state)) #state
        output.append(get_value(zipcode)) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(store[-1]) #phone
        output.append("Pizzeria Limone") #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(store_hours) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
