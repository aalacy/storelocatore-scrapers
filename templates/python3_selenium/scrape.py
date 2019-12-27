import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    driver = get_driver()

    # Begin scraper

    driver.get('https://safegraph.com')
    
    location_name = driver.find_element_by_css_selector('h1.heading-primary').text    

    data.append([
        'https://safegraph.com',
        '<MISSING>'
        location_name,
        '1543 Mission Street',
        'San Francisco',
        'CA',
        '94103',
        'US',
        '<MISSING>',
        '<MISSING>',
        '<MISSING>',
        '<MISSING>',
        '<MISSING>',
        '<MISSING>'
    ])
    
    # End scraper

    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
