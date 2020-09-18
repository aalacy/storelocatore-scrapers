import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.urgentteam.com'

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
    url = "https://www.urgentteam.com/location-map-page"
    session = requests.Session()
    request = session.get(url)
    source = request.text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="view-content"]/div[contains(@class, "views-row ")]')
    data_list = json.loads(validate(source.split('jQuery.extend(Drupal.settings,')[1].split(');</script>')[0]))['geofieldMap']
    geolocation_list = {}
    for key, geo in list(data_list.items()):
        geolocation_list[geo['data']['properties']['description']] = geo['data']['coordinates']         
    for idx, store in enumerate(store_list):
        output = []
        output.append(base_url) # url
        output.append(get_value(store.xpath('.//h2[@class="location-title"]//text()'))) #location name
        output.append(get_value(store.xpath('.//div[@class="street-block"]//text()'))) #address        
        output.append(get_value(store.xpath('.//span[@class="locality"]//text()'))) #city
        output.append(get_value(store.xpath('.//span[@class="state"]//text()'))) #state
        output.append(get_value(store.xpath('.//span[@class="postal-code"]//text()'))) #zipcode
        output.append(get_value(store.xpath('.//span[@class="country"]//text()'))) #country code
        output.append("<MISSING>") #store_number
        output.append(get_value(store.xpath('.//div[@class="location-phone"]//text()'))) #phone
        output.append("Physicians Care | UrgentTeam") #location type
        if output[1] in geolocation_list:
            geolocation = geolocation_list[output[1]]
            output.append(geolocation[1]) #latitude
            output.append(geolocation[0]) #longitude
        else :
            output.append('<MISSING>') #latitude
            output.append('<MISSING>') #longitude
        output.append(get_value(eliminate_space(store.xpath('.//div[@class="location-hours"]//div//text()')))) #opening hours        
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
