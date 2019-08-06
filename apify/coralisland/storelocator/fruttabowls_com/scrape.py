import csv
import re
import pdb
import requests
from lxml import etree
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

options = Options() 
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--start-maximized")
driver = webdriver.Chrome('chromedriver', options=options)

base_url = 'https://www.fruttabowls.com'


def validate(item):
    return item.encode('ascii', 'ignore').encode("utf8").replace(u'\u202d', '').replace(u'\u202c', '').replace(u'\xa0', '').strip()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.fruttabowls.com/find-a-location/"
    driver.get(url)
    source = driver.page_source.encode('ascii', 'ignore').encode("utf8")
    response = etree.HTML(source)
    try:
        temp = response.xpath('//script[@type="application/ld+json"]//text()')[0]
    except:
        pass
    store_hours = response.xpath('//div[@class="locationListItemHours"]')
    store_list = json.loads(temp)['subOrganization']
    for idx, store in enumerate(store_list):    
        output = []
        output.append(base_url) # url
        output.append(store['address']['name']) #location name
        output.append(store['address']['streetAddress']) #address
        output.append(store['address']['addressLocality']) #city
        output.append(store['address']['addressRegion']) #state
        output.append(store['address']['postalCode']) #zipcode
        output.append('US') #country code
        output.append("<MISSING>") #store_number
        output.append(validate(store['telephone'])) #phone
        output.append(store['@type']) #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(' '.join(store_hours[idx].xpath('.//text()'))) #opening hours
        print(output)
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
