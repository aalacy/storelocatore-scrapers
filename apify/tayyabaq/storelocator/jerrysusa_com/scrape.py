import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
                
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('http://jerrysusa.com/store-locator/')
    time.sleep(3)
    stores = driver.find_elements_by_class_name('storepoint-address')
    location = driver.find_elements_by_class_name('storepoint-name')
    location_name = [location[n].text for n in range(0,len(location))]
    for n in range(0,len(stores)):
        a=len(stores[n].text.split(","))
        if a ==5:
            street_address.append(stores[n].text.split(",")[0]+' '+stores[n].text.split(",")[1])
        else:
            street_address.append(stores[n].text.split(",")[0])
    phones = driver.find_elements_by_xpath('//div[@class="storepoint-contact"][2]')
    for n in range(0,len(stores)):
        tagged=usaddress.tag(stores[n].text)[0]
        city.append(tagged['PlaceName'])
        state.append(tagged['StateName'])
        zipcode.append(tagged['ZipCode'])
    for n in range(0,len(phones)):
        if (phones[n].text=='') or (phones[n].text==[]):
            phone.append('<MISSING>')
        else:
            phone.append(phones[n].text)
    for n in range(0,len(street_address)):
        data.append([
            'http://jerrysusa.com',
            'http://jerrysusa.com/store-locator/',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
