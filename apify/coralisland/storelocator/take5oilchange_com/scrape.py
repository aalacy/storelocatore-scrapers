import csv
import re
import pdb
import requests
from lxml import etree
import json

base_url = 'https://www.take5oilchange.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
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
    history = []
    url = "https://www.take5oilchange.com/locations/"
    session = requests.Session()
    source = session.get(url).text    
    response = etree.HTML(source)
    link_list = response.xpath('//a[@class="red__hover-color"]//@href')
    for link in link_list[2:]:
        link = base_url + link
        data = etree.HTML(session.get(link).text)
        store_list = data.xpath('.//div[@class="store-info-item layout-row margin-bottom-2 margin-bottom-1--xs"]')
        if store_list != []:
            for store in store_list:
                detail = validate(store.xpath('./@data-ng-click')).split('vm.setMapClickHandler(')[1].split('})')[0]+'}' 
                detail = re.sub("(\w+):", r'"\1":',  detail.replace("'", '"'))   
                store_hours = ','.join(eliminate_space(store.xpath('.//div[contains(@class, "store-hours")]//text()')))
                store = json.loads(detail)
                output = []
                output.append(base_url) # url
                output.append('Take 5 #' + get_value(store['storeId'])) #location name
                output.append(get_value(store['streetAddress1'])) #address
                output.append(get_value(store['locationCity'])) #city
                output.append(get_value(store['locationState'])) #state
                output.append(get_value(store['locationPostalCode'])) #zipcode
                output.append('US') #country code
                output.append(get_value(store['storeId'])) #store_number
                output.append(get_value(store['phone'])) #phone
                output.append('The Fastest Oil Change on the Planet | Take 5 Oil Change') #location type
                output.append(get_value(store['latitude'])) #latitude
                output.append(get_value(store['longitude'])) #longitude
                output.append(get_value(store_hours)) #opening hours
                if get_value(store_hours) != '<MISSING>':
                    if store['storeId'] not in history:
                        output_list.append(output)
                        history.append(store['storeId'])
        else:
            store_id = validate(data.xpath('//div[@class="fr-store__info col-xs-12 col-sm-6 layout-row layout-column--xs justify-content-between align-items-center flex-wrap"]/@data-storeid'))
            store = json.loads(validate(data.xpath('.//script[@type="application/ld+json"]')[0].xpath('.//text()')))
            output = []
            try:
                output.append(base_url) # url
                output.append(get_value(store['name'])) #location name
                if 'address' in store:
                    output.append(get_value(store['address']['streetAddress'])) #address
                    output.append(get_value(store['address']['addressLocality'])) #city
                    output.append(get_value(store['address']['addressRegion'])) #state
                    output.append(get_value(store['address']['postalCode'])) #zipcode
                    output.append('US') #country code
                    output.append(get_value(store_id)) #store_number
                    output.append(get_value(store['telephone'])) #phone
                    output.append('The Fastest Oil Change on the Planet | Take 5 Oil Change') #location type
                    geo_loc = store['hasMap'].split('loc:')[1].split('+')
                    output.append(get_value(geo_loc[0])) #latitude
                    output.append(get_value(geo_loc[1])) #longitude
                    output.append(get_value(store['openingHours'])) #opening hours
                    if store_id not in history:
                        output_list.append(output)
                        history.append(store_id)     
            except:
                pdb.set_trace()      
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
