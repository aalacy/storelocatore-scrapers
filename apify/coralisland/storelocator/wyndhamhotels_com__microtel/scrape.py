import csv
import re
import pdb
from sgrequests import SgRequests
from lxml import etree
import json
import usaddress
from bs4 import BeautifulSoup
import time
from random import randint
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('wyndhamhotels_com__microtel')



base_url = 'https://www.wyndhamhotels.com'

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    country = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '')
        elif addr[1] == 'CountryName':
            country = addr[0].replace(',', '')
        else:
            street += addr[0].replace(',', '') + ' '

    return { 
            'street': get_value(street), 
            'city' : get_value(city), 
            'state' : get_value(state), 
            'zipcode' : get_value(zipcode),
            'country': get_value(country)
            }

def fetch_data():
    output_list = []
    url = "https://www.wyndhamhotels.com/microtel/locations"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    request = session.get(url)
    time.sleep(randint(1,2))

    response = etree.HTML(request.text)
    store_list = response.xpath('//div[@class="aem-rendered-content"]')[0].xpath('.//div[@class="state-container"]//li[@class="property"]')

    total_links = len(store_list)
    for i, detail_url in enumerate(store_list):        
        logger.info(("Link %s of %s" %(i+1,total_links)))        
        detail_url = 'https://www.wyndhamhotels.com' + validate(detail_url.xpath('.//a')[0].xpath('./@href'))
        detail_request = session.get(detail_url)
        logger.info(detail_url)
        time.sleep(randint(1,2))
        detail = etree.HTML(detail_request.text)
        store_id = validate(detail_request.text.split('var overview_propertyId = "')[1].split('"')[0])
        
        base = BeautifulSoup(detail_request.text,"lxml")

        title = base.find("h1").text.strip()

        all_scripts = base.find_all("script")
        for script in all_scripts:
            script_str = str(script)
            if "latitude" in script_str:
                break

        final_script = script_str[script_str.find("{"):script_str.rfind("}")+1]
        data_json = json.loads(final_script)

        street_address = data_json['address']['streetAddress'].strip()
        city = data_json['address']['addressLocality'].strip()
        try:
            state = data_json['address']['addressRegion'].strip()
        except:
            continue
        zip_code = data_json['address']['postalCode'].strip()

        if street_address == "724 Great Northern Road":
            zip_code = "P6B 5G5"
        country = data_json['address']['addressCountry'].strip()
        if country == "Canada":
            country_code = "CA"
        elif country == "United States":
            country_code = "US"
        phone = data_json['telephone']

        latitude = data_json['geo']['latitude']
        longitude = data_json['geo']['longitude']

        hours = "24 hours open"

        if country_code == "US" or country_code == "CA":
            output = []
            output.append("wyndhamhotels.com") # locator_domain
            output.append(detail_url) # page_url
            output.append(title) #location name
            output.append(street_address) #address
            output.append(city) #city
            output.append(state) #state
            output.append(zip_code) #zipcode
            output.append(country_code) #country code
            output.append(store_id) #store_number
            output.append(phone) #phone
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
