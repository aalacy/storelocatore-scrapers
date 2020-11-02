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
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    driver = get_driver()
    driver.get('http://bigcatchseafoodhouse.com/locations/')
    location = driver.find_elements_by_class_name('custom_html')
    location_name = [location[n].text.split("\n")[0] for n in range(0,len(location),2)]
    for n in range(0,len(location),2):
        city.append(location[n].text.split("\n")[0].split(",")[0])
        state.append(location[n].text.split("\n")[0].split(",")[1])
        try:
            zipcode.append(location[n].text.split("\n")[1].split(",")[-1].split()[1].strip())
            street_address.append(location[n].text.split("\n")[1].split(",")[0])
        except:
            zipcode.append(location[n].text.split("\n")[1].split(",")[-1].split()[-1].strip())
            street_address.append(location[n].text.split("\n")[1].split(".")[0])
    hours_of_operation =[', '.join(location[n].text.split("\n")[3:]) for n in range(0,len(location),2)]
    lat_lon = driver.find_elements_by_xpath('//div[@class="custom_html"]/p/a')
    latitude = [re.findall(r'\@(-?[\d\.]*)', lat_lon[n].get_attribute('href'))[0] for n in range(0,len(lat_lon),2)]
    longitude = [re.findall(r'\,(--?[\d\.]*)', lat_lon[n].get_attribute('href'))[0] for n in range(0,len(lat_lon),2)] 
    phone = [location[n].text.split("\n")[2].replace("Tel:","") for n in range(0,len(location),2)] 
    for n in range(0,len(street_address)): 
        data.append([
            'https://bigcatchseafoodhouse.com',
            'http://bigcatchseafoodhouse.com/locations/',
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
