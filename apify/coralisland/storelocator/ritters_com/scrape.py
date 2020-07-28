import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
import usaddress


base_url = 'https://www.ritters.com'

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.ritters.com/locations.php"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    headers = {'User-Agent' : user_agent}

    session = SgRequests()

    source = session.get(url, headers=headers, verify=False).text
    data = validate(source.split('values:[')[1])
    store_list = eliminate_space(data.split(',],options')[0].split('{latLng:['))
    for store in store_list:
        store_id = validate(store.split('location.php?id=')[1].split('>')[0]).replace("'", "")
        store_link = 'https://www.ritters.com/location.php?id=' + store_id
        print(store_link)
        geo_loc = eliminate_space(store.split(']')[0].split(','))
        store_info = etree.HTML(session.get(store_link,  headers=headers).text)
        output = []
        output.append(base_url) # url
        output.append(store_link) # page url
        is_comming = validate(store_info.xpath('.//div[contains(@class, "coming-soon-label ")]//text()'))
        if is_comming != '' and "Private" not in is_comming:
            continue
        output.append(get_value(store_info.xpath('.//h2//span//text()'))) #location name
        details = eliminate_space(store_info.xpath('.//div[@class="location-info-text"]//text()'))
        if "Private Events" in details[0]:
            output.append("<MISSING>") #address
            city = get_value(store_info.xpath('.//h2//span//text()'))
            output.append(city.split("(")[0].strip())
            if "Houston" in city:
                output.append("TX")
            else:
                output.append("<MISSING>")
            output.append("<MISSING>") #zipcode
            location_type = "Private Events Only"
            geo_loc = ["<MISSING>","<MISSING>"]
        else:
            address_row = 2
            if "," in details[address_row]:
                address_row = 1
            else:
                address_row = 3
            output.append(details[address_row]) #address
            address = details[address_row+1].strip().split(',')
            output.append(address[0]) #city
            output.append(address[1].strip().split(' ')[0]) #state
            output.append(address[1].strip().split(' ')[1]) #zipcode
            location_type = "Main Location"
        output.append('US') #country code
        output.append(store_id) #store_number
        phone = ''
        store_hours = ''
        for de in details:
            if 'Phone:' in de:
                phone = validate(de.replace('Phone:', ''))
        raw_hours = store_info.xpath('.//div[@class="location-info-text"]//p')[-1].xpath('text()')
        store_hours = ""
        for raw_hour in raw_hours:
            if "Phone:" not in raw_hour:
                if " pm" in raw_hour or "-" in raw_hour:
                    store_hours = (store_hours + " " + raw_hour.strip()).strip()
        output.append(get_value(phone)) #phone
        output.append(location_type) #location type
        output.append(get_value(geo_loc[0])) #latitude
        output.append(get_value(geo_loc[1])) #longitude
        output.append(get_value(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
