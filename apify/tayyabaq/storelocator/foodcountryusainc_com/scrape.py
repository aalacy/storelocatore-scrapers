import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

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
    driver.get('https://foodcountryusainc.com/locations')
    location = driver.find_elements_by_class_name('wpgmp_locations_content')
    name = driver.find_elements_by_xpath('//div[@class="wpgmp_location_title"]/a[2]')
    location_name = [name[n].text for n in range(0,len(name))]
    phone = [location[n].text.split("\n")[1].replace("Phone:","") for n in range(0,len(location))]
    street_address = [location[n].text.split("\n")[0] for n in range(0,len(location))]
    for n in range(0,len(street_address)): 
        data.append([
            'https://foodcountryusainc.com',
            'https://foodcountryusainc.com/locations',
            location_name[n],
            street_address[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
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
