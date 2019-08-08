import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
import pandas as pd

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                #Keep the trailing zeroes in zipcodes
                writer.writerow(row)
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\q=(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    #Variables
    data=[]; store_no=[];location_name=[];location_type=[];city=[];street_address=[]; state=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('http://www.speedystop.com/locations.html')
    time.sleep(6)
    # Fetch stores 
    stores = driver.find_elements_by_xpath("//table[@class='tabledivinn']/tbody/tr/td")
    for i in xrange(0,len(stores),4):
        location_name.append(stores[i].text)
        store_no.append(stores[i].text.split("#")[1])
    for i in xrange(1,len(stores),4):
        street_address.append(stores[i].text.split("\n")[0])
        city.append(stores[i].text.split("\n")[1].split(",")[0])
        state.append(stores[i].text.split("\n")[1].split(",")[1])
    for i in xrange(2,len(stores),4):
        phone.append(stores[i].text)
    for i in xrange(3,len(stores),4):
        if stores[i].text!="":
            location_type.append(stores[i].text)
        else:
            location_type.append("<MISSING>")
    for n in range(0,len(location_name)): 
        data.append([
            'http://www.speedystop.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            '<MISSING>',
            'US',
            store_no[n],
            phone[n],
            location_type[n],
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
    
