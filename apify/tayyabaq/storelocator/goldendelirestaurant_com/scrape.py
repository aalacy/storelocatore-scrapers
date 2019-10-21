import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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
    #Variables
    data=[];address_stores=[]; city=[];street_address=[];zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('http://www.goldendelirestaurant.com/locations/')
    time.sleep(6)
    # Fetch stores
    hours = driver.find_elements_by_class_name("g1-list--empty")
    hours_of_operation=[hours[i].text for i in range(0,len(hours))]
    street = driver.find_elements_by_tag_name("h2")
    street_address = [street[i].text for i in range(0,len(street))]
    address =driver.find_elements_by_tag_name("h4")
    for n in range(0,len(address),2):
        city.append(address[n].text.split(",")[0])
        zipcode.append(address[n].text.split(",")[1].strip().split()[-1])
        state.append(address[n].text.split(",")[1].strip().split()[0])
    for n in range(1,len(address),2):
        phone.append(address[n].text)
    for n in range(0,len(street)): 
        data.append([
            'https://www.goldendelirestaurant.com',
            '<MISSING>',
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
