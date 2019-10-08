import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url","location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    data=[];store_number=[]; location_name=[];links=[];countries=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('http://stamart.com/locations.html')
    time.sleep(3)
    stores = driver.find_elements_by_xpath('//img[contains(@src,"images/")]')
    store = [stores[n].get_attribute('alt') for n in range(0,len(stores))]
    for n in range(0,len(store)):
        if (store[n]!='') and (store[n]!=[]):
            location_name.append(store[n])
    loc = driver.find_elements_by_class_name('blacktext')
    for n in range(2,len(loc)):
        store_number.append(loc[n].text.split("\n")[0].split("#")[1])
        street_address.append(loc[n].text.split("\n")[1]+', '+loc[n].text.split("\n")[2])
        city.append(loc[n].text.split("\n")[3].split(",")[0])
        zipcode.append(loc[n].text.split("\n")[3].split(",")[-1].split()[-1])
        st = loc[n].text.split("\n")[3].split(",")[-1].split()[:-1]
        state.append(" ".join(st))
        phone.append(loc[n].text.split("Phone: ")[1].split("\n")[0])
    for n in range(0,len(street_address)):
        data.append([
            'http://stamart.com',
            'http://stamart.com/locations.html',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_number[n],
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
