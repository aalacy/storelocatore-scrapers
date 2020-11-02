import csv
import os
from sgselenium import SgSelenium
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('patelbros_com')



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
    if len(state_zip) == 3:
        state = state_zip[0] + ' ' + state_zip[1]
        zip_code = state_zip[2]
        if len(zip_code) == 4:
            zip_code = '0' + zip_code
    else:
        state = state_zip[0]
        zip_code = state_zip[1]
        if len(zip_code) == 4:
            zip_code = '0' + zip_code
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.patelbros.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    done = False
    for i in range(0, 10):
        locations = driver.find_elements_by_css_selector('div.store-locator__infobox')
        #logger.info(i)
        for loc in locations:
            if loc.text == '':
                continue
            
            addy = loc.find_element_by_css_selector('div.store-address').text.split('\n')
            if '1357 Oaktree Rd' in addy[0]:
                done = True
            
            street_address = addy[0]
            city, state, zip_code = addy_ext(addy[1])
            
            phone_number = loc.find_element_by_css_selector('div.store-tel').text
            if phone_number == '----':
                phone_number = '<MISSING>'
                
            hours = loc.find_element_by_css_selector('div.store-operating-hours').text.replace('\n', ' ').strip()
            if hours == '':
                hours = '<MISSING>'

            goog_href = loc.find_element_by_css_selector('a.infobox__row.infobox__cta.ssflinks').get_attribute('href')
            
            start_idx = goog_href.find('(') + 1
            end_idx = goog_href.find(')')
            
            coords = goog_href[start_idx : end_idx].split(',%20')
            
            lat = coords[0]
            longit = coords[1]

            location_name = '<MISSING>'
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]
            
            # logger.info()
            #logger.info(store_data)
            #logger.info()
            all_store_data.append(store_data)

        if done:
            break
        element = driver.find_element_by_css_selector('a#ssf_next_link')
        driver.execute_script("arguments[0].click();", element)
        time.sleep(2)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
