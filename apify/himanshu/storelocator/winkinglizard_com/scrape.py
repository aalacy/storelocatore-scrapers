import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://winkinglizard.com'

def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    output_list = []
    url = "https://winkinglizard.com/locations"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('.//div[@class="medium-12 columns"]//a[@class="button"]/@href')
    for link in store_list:
        link =   link
        store = etree.HTML(session.get(link).text)
        output = []
        output.append(base_url) # url
        if store.xpath('.//h1//text()') != []:
            output.append(get_value(store.xpath('.//h1//text()'))) #location name
            detail = list(map(lambda s: s.strip(), store.xpath('.//div[@class="medium-6 columns"]')[0].xpath('.//text()') ))
            output.append(detail[2]) #address
            address = detail[3].strip().split(',')
            output.append(address[0]) #city
            output.append(address[1].strip().split(' ')[0]) #state
            zipp = address[1].strip().split(' ')[1]
            output.append(zipp) #zipcode
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            h_temp = ''
            phone = ''
            for idx, hour in enumerate(detail[5:]):
                if 'phone' in hour.lower():
                    phone = detail[idx+6]
                if "44122" in zipp:
                    phone = "(216) 454-0380"
                    break
                h_temp += hour + ' '
            latitude = store.xpath('.//div[@class="medium-6 columns"]//a/@href')[0].split("=")[-1].split(",")[0]
            longitude =store.xpath('.//div[@class="medium-6 columns"]//a/@href')[0].split("=")[-1].split(",")[-1]
            page_url = store.xpath('.//div[@class="medium-6 columns"]//a/@href')[1]
            output.append(phone if phone else "<MISSING>") #phone
            output.append("Winking Lizard Restaurant and Tavern | Winking Lizard") #location type
            output.append(latitude) #latitude
            output.append(longitude) #longitude
            output.append(h_temp.replace("Find Directions  Order Online  Our ","").replace("or until the beer stops flowing (kitchen closes 9:30pm)",'').replace("or until the beer stops flowing (kitchen closes 10pm)",'').replace("or until the beer stops flowing (kitchen closes 9:30pm)",'').replace("or until the beer stops flowing (kitchen closes 10:00pm)",'').replace(" at this time  ",'').replace("or until the beer stops flowing (kitchen closes at 9:30pm)",'').replace("or until the beer stops flowing (kitchen closes at 9:30pm)",'').replace('Hours ','').strip() if h_temp.replace("Find Directions  Order Online  Our ","") else "<MISSING>") #opening hours
            output.append(page_url)
            yield output
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
