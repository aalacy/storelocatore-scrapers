import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.texashealth.org/'
    ext = 'Locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    radius = driver.find_element_by_xpath('//*[@data-value="50"]')
    radius.click()

    driver.implicitly_wait(5)

    select = Select(driver.find_element_by_id('DropDownOptions'))

    opts = driver.find_element_by_id('DropDownOptions').find_elements_by_css_selector('option')
    opt_list = []
    for opt in opts:
        opt_list.append(opt.text.strip())

    all_store_data = []
    for i, opt in enumerate(opt_list):
        if i == 0:
            continue
            
        select.select_by_index(i)
        driver.implicitly_wait(5)
        time.sleep(5)
        
        more = driver.find_element_by_css_selector('div.load-more')
        while more.get_attribute('style') != 'display: none;':
            
            more.find_element_by_css_selector('input').click()
            driver.implicitly_wait(5)
            time.sleep(2)
            more = driver.find_element_by_css_selector('div.load-more')
            
        locs = driver.find_element_by_css_selector('ul.search-result-list').find_elements_by_css_selector('li')
        
        for loc in locs:
            longit = loc.get_attribute('data-longitude')
            lat = loc.get_attribute('data-latitude')
            
            location_name = loc.find_element_by_css_selector('div.field-navigationtitle').text
            street_address = loc.find_element_by_css_selector('div.field-address-line-1').text
            street_address = street_address.split('Ste ')[0].split(' Suite ')[0].replace(',', '')

            city = loc.find_element_by_css_selector('span.field-city').text.replace(',', '').strip()
            state = loc.find_element_by_css_selector('span.field-state').text.strip()
            zip_code = loc.find_element_by_css_selector('span.field-zip-code').text
            
            phone_number = loc.find_element_by_css_selector('a.field-phone-number').text
            
            page_url = loc.find_element_by_css_selector('div.button-primary').find_element_by_css_selector('a').get_attribute('href')
            
            country_code = 'US'
            location_type = opt.split('(')[0].strip()
            hours = '<MISSING>'
            store_number = '<MISSING>'
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
            
            all_store_data.append(store_data)
            
        time.sleep(1)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
