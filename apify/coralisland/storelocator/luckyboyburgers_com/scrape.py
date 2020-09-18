import csv
import re
from lxml import etree
import json
import phonenumbers
from sgrequests import SgRequests

base_url = 'http://luckyboyburgers.com'

def is_phone(x):
    try:
        return phonenumbers.is_valid_number(phonenumbers.parse(x, "US"))
    except:
        return False

def validate(item):
    if type(item) == list:
        item = ' '.join(item)
    while True:
        if item[-1:] == ' ':
            item = item[:-1]
        else:
            break
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

def is_store(store):
    info = eliminate_space(store.xpath(".//text()"))
    phones = [x for x in info if is_phone(x)]
    return len(phones) > 0

def fetch_data():
    session = SgRequests()
    output_list = []
    url = "http://luckyboyburgers.com/location"
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="sqs-block-content"]')
    store_list = [store for store in store_list if is_store(store)]
    lat_lng_json = response.xpath('//div[contains(@data-block-json, "mapLat")]/@data-block-json')
    for store, geoinfo in zip(store_list, lat_lng_json):
        info = eliminate_space(store.xpath(".//text()")) 
        phone = [x for x in info if is_phone(x)][0] 
        phone_index = info.index(phone)
        parsed = json.loads(geoinfo)['location']
        street = parsed['addressLine1']
        csz = parsed['addressLine2'].split(',')
        city = csz[0].strip()
        state = csz[1].strip()
        zipcode = csz[2].strip()
        latitude = parsed['mapLat']
        longitude = parsed['mapLng']
        title = parsed['addressTitle'] 
        hours = ' '.join(info[phone_index+1:])
        output = []
        output.append(base_url) # url
        output.append(title) #location name
        output.append(street) #address
        output.append(city) #city
        output.append(state) #state
        output.append(zipcode) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(phone) #phone
        output.append("Lucky Boy Burgers") #location type
        output.append(latitude) #latitude
        output.append(longitude) #longitude
        output.append(hours) #opening hours

        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
