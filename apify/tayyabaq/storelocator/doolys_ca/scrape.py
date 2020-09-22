import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time

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
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[]
    driver=get_driver()
    driver.get("https://www.doolys.ca/locations-1")
    time.sleep(15)
    store=driver.find_elements_by_xpath(('//footer[@id="footer"]/div/div[2]/div/div/div'))
    for n in range(0,len(store)):
        if store[n].text!="":
            location_name.append(store[n].text.split("\n")[0].split("|")[0])
            street_address.append(store[n].text.split("\n")[1].split(",")[0])
            city.append(store[n].text.split("\n")[1].split(",")[1])
            state.append(store[n].text.split("\n")[1].split(",")[2].split()[0].strip())
            phone.append(store[n].text.split("\n")[-1].split("|")[0].strip())
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.doolys.ca',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            '<MISSING>',
            'Canada',
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
