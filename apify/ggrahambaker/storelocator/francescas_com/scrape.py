import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():    
    locator_domain = 'https://www.francescas.com/'
    ext = 'store-locator/all-stores.do'

    driver = get_driver()
    driver.get(locator_domain + ext)



    #close = driver.find_element_by_xpath('//img[@aria-label="Popup Close Button"]')
    #driver.execute_script("arguments[0].click();", close)

    link_list = []
    locs = driver.find_elements_by_css_selector('div.eslStore.ml-storelocator-headertext')
    for loc in locs:
        link = loc.find_element_by_css_selector('a').get_attribute('href')
        
        if link == '':
            continue
        
        if link in link_list:
            continue
            
        link_list.append(link)
        
    all_store_data = []
    for i, link in enumerate(link_list):

        driver.get(link)
        driver.implicitly_wait(10)

        try:
            location_name = driver.find_element_by_xpath('//span[@itemprop="name"]').text
        
        except NoSuchElementException:
            continue

        store_number = location_name.split('#')[1]
        
        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text.replace('\n', ' ')
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text
        if len(zip_code) == 4:
            zip_code = '0' + zip_code
        hours = driver.find_element_by_css_selector('span.ml-storelocator-hours-details').text.replace('\n', ' ')

        try:
            phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text
        except NoSuchElementException:
            phone_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        country_code = 'US'
        location_type = '<MISSING>'
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

        



    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
