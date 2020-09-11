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

base_url = 'https://eurekarestaurantgroup.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://eurekarestaurantgroup.com/locations"
    session = requests.Session()
    request = session.get(url)
    response = etree.HTML(request.text)
    store_list = response.xpath('//ul[@class="dropdown-menu"]')[0].xpath('.//li/a/@href')
    for store in store_list:
        driver.get(store)
        source = driver.page_source
        data = etree.HTML(source)   
        try:
            temp = data.xpath('//script[@class="yext-schema-json"]//text()')[0]
        except:
            pass
        detail = json.loads(temp)
        output = []
        output.append(base_url) # url
        output.append('<MISSING>') #location name
        output.append(detail['address']['streetAddress']) #address
        output.append(detail['address']['addressLocality']) #city
        output.append(detail['address']['addressRegion']) #state
        output.append(detail['address']['postalCode']) #zipcode
        output.append(detail['address']['addressCountry']) #country code
        output.append("<MISSING>") #store_number
        output.append(detail['telephone']) #phone
        output.append("Restaurants") #location type
        output.append(detail['geo']['latitude']) #latitude
        output.append(detail['geo']['longitude']) #longitude
        openingHoursSpecification = detail['openingHoursSpecification']
        openingHours = ''
        if openingHoursSpecification:
            for hour in openingHoursSpecification:
                openingHours += hour['dayOfWeek'] + ' ' + hour['opens'] + ' - ' +  hour['closes'] + ', '
            openingHours= openingHours[:-2]
        output.append(openingHours) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
