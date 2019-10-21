import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
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
    driver.get('http://www.farmstores.com/locations/')
    time.sleep(3)
    stores = driver.find_elements_by_class_name('location-address')
    for n in range(0,len(stores)-1):
        try:
            city.append(stores[n].text.split(",")[1])
            street_address.append(stores[n].text.split(",")[0])
            state.append(stores[n].text.split(",")[2].split()[0])
            zipcode.append(stores[n].text.split(",")[2].split()[1])
        except:
            street_address.append(stores[n].text.split("ave")[0]+' ave')
            city.append(stores[n].text.split()[-3])
            state.append(stores[n].text.split()[-2])
            zipcode.append(stores[n].text.split()[-1])
    loc = driver.find_elements_by_class_name('loc-title')
    location_name = [loc[n].text for n in range(0,len(loc))]
    hours = driver.find_elements_by_class_name('location-hours')
    hours_of_operation = [hours[n].text for n in range(0,len(hours))]
    phones = driver.find_elements_by_class_name('location')
    for n in range(0,len(phones)):
        if 'Phone' in phones[n].text:
            phone.append(phones[n].text.split("\n")[3].split('Phone:')[1].strip())
        else:
            phone.append('<MISSING>')
    for n in range(0,len(street_address)): 
        data.append([
            'https://www.farmstores.com',
            'http://www.farmstores.com/locations/',
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
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
