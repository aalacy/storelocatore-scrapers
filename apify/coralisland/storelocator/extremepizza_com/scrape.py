import csv
import re
import pdb
import requests
from lxml import etree
import json

from selenium import webdriver

base_url = 'https://www.extremepizza.com'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

def validate(items):
    rets = []
    for item in items:
        item = item.replace(u'\xa0', '').replace(u'\u2019', '').replace(u'\u202d', '').strip()
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
    url = "https://www.extremepizza.com/store-locator/"
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
        output.append(store['telephone']) #phone
        output.append(store['@type']) #location type
        output.append("<MISSING>") #latitude
        output.append("<MISSING>") #longitude
        output.append(' '.join(store_hours[idx].xpath('.//text()')[1:])) #opening hours
        output_list.append(validate(output))
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
