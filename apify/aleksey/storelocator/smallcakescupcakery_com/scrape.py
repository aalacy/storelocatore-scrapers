import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
            
def parse_geo(url):
    return re.compile(r"lat=([0-9\-\.]+)\&lon=([0-9\-\.]+)").split(url)

def parse_node(store_el, className):
    parent_name = 'span.' + className
    parent = store_el.find_element_by_css_selector(parent_name).get_attribute('textContent')
    child_name = 'span.' + className + ' span'
    child = store_el.find_element_by_css_selector(child_name).get_attribute('textContent')
    return parent.replace(child, '')

def fetch_data():
    data = []
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
    driver = webdriver.Chrome('chromedriver', options=options)
    # driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)
    driver.get('https://www.smallcakescupcakery.com/locations/')
    store_els = driver.find_elements_by_css_selector('div.location-item')
 
    for store_el in store_els:
        try:
            phone = store_el.find_element_by_css_selector('span.phone').get_attribute('textContent')
        except NoSuchElementException:
            phone = '<MISSING>'
        zipcode = parse_node(store_el, 'location-zip')
        if (zipcode == ''):
            zipcode = '<MISSING>'    
        state = parse_node(store_el, 'location-state')    
        city = parse_node(store_el, 'location-city')
        street_address = parse_node(store_el, 'location-address')
 
        location_name = parse_node(store_el, 'location-locale')
        if (location_name == ''):
            location_name = '<MISSING>'    

        lat = parse_geo(store_el.find_element_by_css_selector('span.map-btn a').get_attribute('href'))[1]
        lon = parse_geo(store_el.find_element_by_css_selector('span.map-btn a').get_attribute('href'))[2]
        if(street_address != ''):    
            data.append([
                'https://www.smallcakescupcakery.com',
                location_name,
                street_address,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone,
                '<MISSING>',
                lat,
                lon,
                '<MISSING>'
            ])
    driver.quit()
    return data

def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)

scrape()