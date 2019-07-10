import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    # options = Options() 
    # options.add_argument('--headless')
    # options.add_argument('--no-sandbox')
    # options.add_argument('--disable-dev-shm-usage')
    # driver = webdriver.Chrome('/bin/chromedriver', chrome_options=options)
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')
    driver.get('https://www.brandymelvilleusa.com/locations')
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
