from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re
from sgrequests import SgRequests
from lxml import etree

from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thecamptc_com')



base_url = 'https://www.thecamptc.com'

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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    output_list = []
    url = "https://www.thecamptc.com/locations.php"
    source = session.get(url).text
    response = etree.HTML(source)
    store_list = response.xpath('//a[@class="location-btn"]')
    for store_link in store_list:
        city_state = eliminate_space(validate(store_link.xpath('.//text()')).split(' '))
        store_link = validate(store_link.xpath('./@href'))
        if "mexicali" in store_link:
            continue
        logger.info(store_link)
        store = etree.HTML(session.get(store_link).text)
        output = []
        raw_address = eliminate_space(store.xpath('.//div[@class="location-details"][1]//text()'))
        if raw_address:
            raw_hours = eliminate_space(store.xpath('.//div[@class="location-details"][2]//text()'))[1:]
            phone = get_value(re.findall("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}", ', '.join(raw_address))[0])                
            zipcode = get_value(re.findall("\d{5}", ', '.join(raw_address))[-1])
            output.append(base_url) # url
            output.append(store_link) # page_url
            output.append(', '.join(city_state)) #location name
            output.append(raw_address[1]) #address
            output.append(raw_address[2].split('\n')[0].replace(",","")) # city
            output.append(raw_address[2].split('\n')[1].strip()) # state
            output.append(zipcode) #zipcode 
            output.append('US') #country code
            output.append("<MISSING>") #store_number
            output.append(phone) #phone
            output.append("<MISSING>") #location type
            geo_loc = validate(store.xpath('.//iframe/@src')).split('!2d')[1].split('!2m')[0].split('!3d')
            lat = geo_loc[1]
            if len(lat) > 30:
                lat = lat[:lat.find("!")]
            output.append(lat) #latitude
            output.append(geo_loc[0]) #longitude
            output.append(validate(' '.join(raw_hours))) #opening hours            
        else:
            if store_link == "https://thecamptc.com/locations/cool-springs-tennessee":
                driver = SgSelenium().chrome()
                time.sleep(2)

                driver.get(store_link)
                time.sleep(randint(6,8))

                base = BeautifulSoup(driver.page_source,"lxml")
                raw_address = base.footer.find(id="text-2").text.split("\n")
                phone = raw_address[0].replace("CONTACT US","").strip()
                raw_hours = base.footer.find(id="text-3").text.replace("CLASS HOURS","").replace("\n"," ").replace("\xa0","")
                if "Pandemic" in raw_hours:
                    raw_hours = raw_hours[raw_hours.find(":")+1:].strip()
                zipcode = get_value(re.findall("\d{5}", ', '.join(raw_address))[-1])
                output.append(base_url) # url
                output.append(store_link) # page_url
                output.append(', '.join(city_state)) #location name
                output.append(raw_address[1].strip()) #address
                output.append(raw_address[2].split(',')[0].replace(",","")) # city
                output.append(raw_address[2].split(' ')[1].strip()) # state
                output.append(zipcode) #zipcode
                output.append('US') #country code
                output.append("<MISSING>") #store_number
                output.append(phone) #phone
                output.append("<MISSING>") #location type
                geo_loc = base.find("iframe")['src'].split('!2d')[1].split('!2m')[0].split('!3d')
                lat = geo_loc[1]
                if len(lat) > 30:
                    lat = lat[:lat.find("!")]
                output.append(lat) #latitude
                output.append(geo_loc[0]) #longitude
                output.append(raw_hours) #opening hours
                driver.close()
        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
