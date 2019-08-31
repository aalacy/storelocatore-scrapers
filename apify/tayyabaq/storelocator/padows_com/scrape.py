import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    driver.get('http://www.padows.com/LCTN.html')
    location = driver.find_elements_by_xpath('//div[@id="locations-content"]/ul/li')
    street_address = [location[n].text.split("-")[1].strip().split(",")[0] for n in range(0,len(location))]
    location_name = [location[n].text for n in range(0,len(location))]
    phones = driver.find_elements_by_xpath('//div[@id="locations-content"]/ul/ul/li[1]')
    hour = driver.find_elements_by_xpath('//div[@id="locations-content"]/ul/ul/li[2]')
    hours_of_operation =[hour[n].text for n in range(0,len(hour))]
    for n in range(0,len(phones)):
        if 'p.m.' not in phones[n].text:
            phone.append(phones[n].text) 
    for n in range(0,len(street_address)): 
        data.append([
            'http://www.padows.com',
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
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
