import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from lxml import etree
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hcoafitness_com')



base_url = 'https://www.hcoafitness.com'

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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    output_list = []
    url = "https://www.hcoafitness.com/locations?lang=en"
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = json.loads(request.text.split('$("#map1").maps(')[1].split(').data')[0])["places"]

    store_htmls = response.xpath('.//div[contains(@class, "location-box")]')
    store_data = {}
    for store_html in store_htmls:
        detail_url = validate(store_html.xpath(".//a/@href")[0])
        logger.info(detail_url)
        detail_request = session.get(detail_url)
        detail = BeautifulSoup(detail_request.text,"lxml")

        phone = detail.find(class_="page-caption-phone-mobile").text.strip()
        title = 'HCOA Fitness ' + detail.h1.text.replace("– Unisex","").replace("Ciudad","Bayamón Ciudad").strip()
        hours = detail.find(class_="gdlr-core-opening-hour-list").text.replace("pm","pm ").replace("Thurs","Thu").replace("Thu","Thu ").replace("Fri","Fri ").replace("Sat","Sat ").replace("Sun","Sun ").strip()
        address = validate(eliminate_space(store_html.xpath('.//div[@class="gdlr-core-feature-box-item-content"]/p//text()'))[:2])
        store_data[title] = {"detail_url": detail_url, "phone": phone, "hours": hours, "address": address}

    poi_done = []
    for store in store_list:
        title = validate(store['title'])
        poi_done.append(title)            
        index = title
        address = store_data[index]["address"]
        output = []
        output.append(base_url) # url
        output.append(store_data[index]['detail_url']) # url
        output.append(title.replace('HCOA Fitness ', '')) #location name
        output.append(address) #address
        output.append(validate(store['location']['city'])) #city
        output.append("PR") #state
        output.append(validate(store['location']['postal_code'])) #zipcode
        output.append("US") #country code
        output.append(validate(store['id'])) #store_number
        
        output.append(store_data[index]['phone']) #phone
        output.append("<MISSING>") #location type
        output.append(validate(store['location']['lat'])) #latitude
        output.append(validate(store['location']['lng'])) #longitude
        output.append(store_data[index]['hours']) #opening hours
        output_list.append(output)

    if "HCOA Fitness Santurce" not in poi_done:
        title = "HCOA Fitness Santurce"
        index = title
        address = store_data[index]["address"]
        output = []
        output.append(base_url) # url
        output.append(store_data[index]['detail_url']) # url
        output.append(title.replace('HCOA Fitness ', '')) #location name
        output.append(address) #address
        output.append(validate("San Juan")) #city
        output.append("PR") #state
        output.append(validate("00909")) #zipcode
        output.append(validate("US")) #country code
        output.append(validate("<MISSING>")) #store_number
        
        output.append(store_data[index]['phone']) #phone
        output.append("<MISSING>") #location type
        output.append("18.4498665") #latitude
        output.append("-66.0772129") #longitude
        output.append(store_data[index]['hours']) #opening hours
        output_list.append(output)

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
