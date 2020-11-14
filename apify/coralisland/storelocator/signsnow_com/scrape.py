import csv
import re
from sgrequests import SgRequests
from lxml import etree
import json

base_url = 'https://www.signsnow.com'

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

def parse_address(addr):
    street = addr[0].strip()
    city = addr[1].strip()
    state = addr[2].split()[0].strip()
    zipcode = " ".join(addr[2].split()[1:]).strip().replace(">","")

    if "All Of East Tennessee" in street:
        street = '<MISSING>'
        city = 'Morristown'
    return { 
        'street': street,
        'city' : city, 
        'state' : state, 
        'zipcode' : zipcode
    }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    output_list = []
    url = "https://www.signsnow.com/all-locations"
    history = []
    page_url = ''
    source = session.get(url).text    
    response = etree.HTML(source)
    store_list = response.xpath('//div[@class="innerbody"]//a/@href')
    for store_link in store_list:
        if store_link != 'http://www.signsnow.co.uk' and store_link not in history:
            history.append(store_link)
            if 'http' not in store_link:
                store_link = base_url + store_link
            store = etree.HTML(session.get(store_link).text)
            output = []
            output.append(base_url) # url
            output.append(store_link) # page url
            output.append(get_value(store.xpath('.//p[@class="location-name"]//text()'))) #location name
            address = eliminate_space(store.xpath('.//p[@class="contact"]//text()'))[0].split("|")

            script = store.xpath('.//script[@type="application/ld+json"]//text()')[0].replace('\n', '').strip()
            store_js = json.loads(script)

            latitude = store_js['geo']['latitude']
            longitude = store_js['geo']['longitude']
            hours = store_js['openingHours']

            if address[-1][-2:] != 'GB':
                if address[-1][-2:] != 'CA':
                    country = "US"
                else:
                    address = eliminate_space(store.xpath('.//p[@class="contact"]//text()'))[0].replace("CA","").split("|")                    
                    country = "CA"
                address = parse_address(address)
                output.append(address['street']) #address
                output.append(address['city']) #city
                output.append(address['state']) #state
                output.append(address['zipcode']) #zipcode  
                output.append(country) #country code
                output.append("<MISSING>") #store_number
                output.append(get_value(store.xpath('.//p[@class="phone"]//text()'))) #phone
                output.append("<MISSING>") #location type
                output.append(latitude) #latitude
                output.append(longitude) #longitude
                output.append(hours) #opening hours
                output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
