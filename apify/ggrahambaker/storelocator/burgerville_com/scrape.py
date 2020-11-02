import csv
import os
from sgselenium import SgSelenium
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('burgerville_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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
    locator_domain = 'https://www.burgerville.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    loc_list = driver.find_element_by_id('map_sidebar_toggle')
    driver.execute_script("arguments[0].click();", loc_list)

    main = driver.find_element_by_id('map_sidebar')
    locs = main.find_elements_by_css_selector('div.results_wrapper')
    all_store_data = []
    for l in locs:
        loc_name = l.find_element_by_css_selector('span.location_name')
        driver.execute_script("arguments[0].click();", loc_name)
        time.sleep(2)

        street_address = driver.find_element_by_css_selector('span#slp_bubble_address').text + ' '
        street_address += driver.find_element_by_css_selector('span#slp_bubble_address2').text
        street_address = street_address.strip()

        city = driver.find_element_by_css_selector('span#slp_bubble_city').text
        state = driver.find_element_by_css_selector('span#slp_bubble_state').text
        zip_code = driver.find_element_by_css_selector('span#slp_bubble_zip').text
        phone_number = driver.find_element_by_css_selector('span#slp_bubble_phone').text.replace('Phone', '').strip()

        hours = driver.find_element_by_css_selector('span.location_detail_hours').text.replace('\n', ' ').replace('\\n', ' ').strip()

        cont = l.text.split('\n')
        cut = cont[0].find('(')
        location_name = cont[0][:cut].strip()
        if 'Signature' in cont[0]:
            store_number = '<MISSING>'
        else:
            store_number = cont[0][cut + 1:-1].replace('#', '')

        country_code = 'US'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        logger.info(store_data)
        all_store_data.append(store_data)
        time.sleep(2)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
