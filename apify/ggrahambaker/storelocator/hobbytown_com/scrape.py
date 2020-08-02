import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from random import randint
import re


def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.hobbytown.com/'
    ext = 'store-locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    cityinput = driver.find_element_by_id('CityState')
    cityinput.clear()
    cityinput.send_keys( "Iowa City" )

    time.sleep(5)

    to_click = driver.find_element_by_css_selector('div.ui-menu-item-wrapper')
    driver.execute_script("arguments[0].click();", to_click)
    time.sleep(2)

    select = Select(driver.find_element_by_id('radius'))
    select.select_by_value('3000')

    time.sleep(5)

    hrefs = driver.find_elements_by_xpath('//a[@title="Store Profile"]')

    link_list = []
    for h in hrefs:
        link = h.get_attribute('href')
        link_list.append(link)
      
    all_store_data = []
    for link in link_list:
        print(link)
        driver.get(link)
        driver.implicitly_wait(5)
        time.sleep(1)
        
        location_name = driver.find_element_by_css_selector('h1.titlebar').find_element_by_css_selector('span').text
        
        addy = driver.find_element_by_css_selector('div.address').text.split('\n')
        street_address = ' '.join(addy[:-1])
        city, state, zip_code = addy_ext(addy[-1])
        
        phone_number = driver.find_element_by_css_selector('div.phone').text.replace('+1', '').strip()
        
        hour_tds = driver.find_element_by_css_selector('div.hours').find_element_by_css_selector('tbody').find_elements_by_css_selector('td')#.replace('\n', ' ')
        hours = ''
        for td in hour_tds:
            hours += td.text + ' '
            
        hours = hours.strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        page_url = link

        try:
            element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                (By.ID, "map")))
            time.sleep(randint(1,2))
            try:
                map_frame = driver.find_element_by_id("map").find_element_by_tag_name("iframe")
                driver.switch_to.frame(map_frame)
                time.sleep(randint(1,2))
                map_str = driver.page_source
                geo = re.findall(r'\[[0-9]{2}\.[0-9]+,-[0-9]{2}\.[0-9]+\]', map_str)[0].replace("[","").replace("]","").split(",")
                lat = geo[0]
                longit = geo[1]
            except:
                lat = '<MISSING>'
                longit = '<MISSING>'
        except:
            lat = "<MISSING>"
            longit = "<MISSING>"

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
