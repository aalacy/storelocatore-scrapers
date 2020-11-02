import csv
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    driver.get('https://coopersfoodsmn.com')
    location = driver.find_elements_by_class_name('location-data')
    street_address = [location[n].text.split("\n")[1] for n in range(0,len(location))]
    location_name = [location[n].text.split("\n")[0] for n in range(0,len(location))]
    hours_of_operation =[location[n].text.split("\n")[-2] for n in range(0,len(location))]
    city = [location[n].text.split("\n")[2].split(",")[0] for n in range(0,len(location))]
    state = [location[n].text.split("\n")[2].split(",")[1].split()[0].strip() for n in range(0,len(location))]
    zipcode =[location[n].text.split("\n")[2].split(",")[1].split()[1].strip() for n in range(0,len(location))]
    latitude = [location[n].get_attribute('data-lat') for n in range(0,len(location))]
    longitude = [location[n].get_attribute('data-lon') for n in range(0,len(location))] 
    phone = [location[n].text.split("\n")[3].replace("Phone:","") for n in range(0,len(location))] 
    for n in range(0,len(street_address)): 
        data.append([
            'https://coopersfoodsmn.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
