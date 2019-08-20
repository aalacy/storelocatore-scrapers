import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import re


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://ilovejuicebar.com/'
    ext = 'locations-1'

    driver = get_driver()
    driver.get(locator_domain + ext)
    states = driver.find_elements_by_css_selector('section.Index-page')
    link_list = []
    for state in states:
        hrefs = state.find_elements_by_css_selector('a')
        for href in hrefs:
            if 'locations-1' not in href.get_attribute('href'):
                link_list.append(href.get_attribute('href'))




    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
