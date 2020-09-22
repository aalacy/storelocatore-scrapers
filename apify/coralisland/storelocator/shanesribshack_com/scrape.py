import csv
import re
from lxml import etree
import json
import usaddress
from sgrequests import SgRequests

base_url = 'https://www.shanesribshack.com'

def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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
            state = addr[0].replace(',', '')
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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.shanesribshack.com/locations/"
    session = SgRequests()
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Cookie': 'ARRAffinity=c56588c17a93aaac773652dc3876586afcaa27360b8b3b216d847fbd3a031f74; curLat=34.0456390380859; curLong=-118.241638183594; ip_Store=Glendale; myShanes=1793; locationName=Hartsfield-Jackson International Airport; userSet=true',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
    }
    source = session.get(url, headers=headers).text
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="col-sm-6 padded-1"]')
    for store in store_list:
        output = []
        output.append(base_url) # url
        store_name = validate(store.xpath('.//h3//text()'))
        output.append(store_name) #location name
        if 'coming' not in store_name.lower():
            details = eliminate_space(store.xpath('.//p//text()'))
            address = ''
            phone = ''
            for idx, de in enumerate(details):
                if 'phone' in de.lower():
                    address = ', '.join(details[:idx])
                    phone = details[idx+1]       
            address = parse_address(address)
            output.append(address['street']) #address
            output.append(address['city']) #city
            output.append(address['state']) #state
            output.append(address['zipcode']) #zipcode  
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(get_value(phone)) #phone
            output.append("Shane's Rib Shack") #location type
            links = eliminate_space(store.xpath('.//a/@href'))
            geo_loc = [l for l in links if 'google.com' in l][0].split('/@')
            if len(geo_loc) > 1:
                geo_loc = geo_loc[1].split(',/data')[0].split(',')
                output.append(geo_loc[0]) #latitude
                output.append(geo_loc[1]) #longitude
            else:
                output.append('<INACCESSIBLE>') #latitude
                output.append('<INACCESSIBLE>') #longitude
            page_url = base_url+[l for l in links if '/locations' in l][0]
            details = etree.HTML(session.get(page_url).text)
            store_hours = validate(details.xpath('.//span[@class="d-block"]')[-2].xpath('.//text()'))
            output.append(get_value(store_hours)) #opening hours
            output.append(page_url) #page_url
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
