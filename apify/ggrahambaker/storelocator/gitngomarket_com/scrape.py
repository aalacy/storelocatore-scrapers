import csv
import os
from sgselenium import SgSelenium
import time

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
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
    locator_domain = 'https://gitngomarket.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    height = driver.execute_script("return document.body.scrollHeight")
    step = 0
    while True:
        # Scroll down to bottom
        step += 200
        driver.execute_script("window.scrollTo(0, " + str(step) + ");")

        time.sleep(SCROLL_PAUSE_TIME)
        if step > height:
            break
    all_store_data = []
    main = driver.find_element_by_css_selector(
        'div.et_pb_section.et_pb_section_1.et_pb_with_background.et_section_regular')
    rows = main.find_elements_by_css_selector('div.et_pb_row')
    for row in rows:
        addy = row.find_element_by_css_selector('div.map-addr').text.split('\n')
        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])

        phone_number = row.find_element_by_css_selector('div.map-text').find_element_by_css_selector('a').text

        hours = row.find_element_by_css_selector('div.map-hours').text.replace('\n', ' ')

        map_div = row.find_element_by_css_selector('div.et_pb_map')
        lat = map_div.get_attribute('data-center-lat')
        longit = map_div.get_attribute('data-center-lng')
    
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        
        store_number = '<MISSING>'
        location_name = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
