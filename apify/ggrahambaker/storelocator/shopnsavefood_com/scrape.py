import csv
import os
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shopnsavefood_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.shopnsavefood.com/' 
    ext = 'StoreLocator/Search/?ZipCode=10001&miles=10000'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#StoreLocator')
    rows = main.find_elements_by_css_selector('a')
    link_list = [a.get_attribute('href') for a in rows]

    all_store_data = []
    for link in link_list:
        logger.info(link)
        driver.get(link)
        driver.implicitly_wait(10)
        location_name = driver.find_element_by_css_selector('h3').text
        addy = driver.find_element_by_css_selector('p.Address').text.split('\n')
        street_address = addy[1]
        city, state, zip_code = addy_ext(addy[2])
        phone_number = driver.find_element_by_css_selector('p.PhoneNumber').find_element_by_css_selector('a').text
        hours = driver.find_element_by_css_selector('table#hours_info-BS').text.replace('Hours of Operation:', '').strip().replace('\n', ' ')
        
        hours = hours.split('Store')[0]
        country_code = 'US'
        lat = '<MISSING>'
        longit = '<MISSING>'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        page_url = link

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        logger.info(store_data)
        logger.info()
        logger.info()
        
        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
