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
                rows = tuple("=\"" + str(r) + "\"" for r in row)
                writer.writerow(rows)
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def parse_geo(url):
    lon = re.findall(r'(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def fetch_data():
    #Variables
    data=[]; latitude=[];longitude=[];zipcode=[];location_name=[];location_type=[];city=[];street_address=[]; state=[]; phone=[]
    #Driver
    driver = get_driver()
    #Get site
    driver.get('https://studiothree.com/')
    time.sleep(6)
    # Fetch stores
    stores=driver.find_elements_by_class_name("two-col-f")
    loc=driver.find_elements_by_link_text("DIRECTIONS")
    for n in range(0,len(stores)-2):
        location_name.append(stores[n].text.split("\n")[0])
        street_address.append(stores[n].text.split("\n")[1])
        city.append(stores[n].text.split("\n")[2].split(", ")[0])
        state.append(stores[n].text.split("\n")[2].split(",")[1].split()[0])
        zipcode.append(stores[n].text.split("\n")[2].split(",")[1].split()[1])
        phone.append(stores[n].text.split("\n")[3])
        lat, lon = parse_geo(loc[n].get_attribute('href'))
        latitude.append(lat)
        longitude.append(lon)
    for n in range(0,len(location_name)): 
        data.append([
            'https://studiothree.com/',
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
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
    
