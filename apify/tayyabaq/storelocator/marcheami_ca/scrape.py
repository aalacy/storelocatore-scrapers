import csv
import os
import re, time
import requests
from bs4 import BeautifulSoup
import json
import lxml.html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    driver = get_driver()
    data=[];page_url=[];hours_of_operation=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[]
    url = "http://marcheami.ca/siteamienglish/index.php"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    doc = lxml.html.fromstring(r.content)
    store = doc.xpath('//ul[@class="rvnavigator"]/li[4]/ul/li/a/@href')
    states = doc.xpath('//ul[@class="rvnavigator"]/li[4]/ul/li/a/span/text()')
    for n in range(0,len(store)):
        driver.get(store[n])
        time.sleep(4)
        name = driver.find_elements_by_xpath('//div[@class="store"]/h2')
        address =  driver.find_elements_by_xpath('//div[@class="store"]/ul/li[1]')
        phones =  driver.find_elements_by_xpath('//div[@class="store"]/ul/li[3]')
        for m in range(0,len(address)):
            location_name.append(name[m].text)
            street_address.append(address[m].text)
            state.append(states[n])
            phone.append(phones[m].text)
            page_url.append(store[n])
    for n in range(0,len(location_name)): 
        data.append([
            'https://marcheami.ca/',
            page_url[n],
            location_name[n],
            street_address[n],
            '<MISSING>',
            state[n],
            '<MISSING>',
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
