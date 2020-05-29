import csv
import os
from sgselenium import SgSelenium
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.krispykreme.ca/'
    ext = 'find-a-store/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    time.sleep(4)
    driver.implicitly_wait(30)

    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_len = 100
    while scroll_len < last_height:
        # Scroll down to bottom
        
        driver.execute_script("window.scrollTo(0, " + str(scroll_len) + ")")
        scroll_len += 50
        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

    locs = driver.find_elements_by_css_selector('div.location')

    all_store_data = []
    for loc in locs:
        
        cont = loc.text.split('\n')
  
        if len(cont) == 12:
            off = 1
        else:
            off = 0

        location_name = cont[0]
        street_address = cont[1].split('(')[0].strip()

        city_state = cont[off + 2].split(' ')
        if len(city_state) == 3:
            city = city_state[0] + ' ' + city_state[1]
            state = city_state[2]
        else:
            city = city_state[0]
            state = city_state[1]
        
        zip_code = cont[off + 3]
        
        phone_number = cont[off + 5].replace('Tel:', '').strip()

        hours = ''
        for h in cont[off + 6:]:
            hours += h + ' '
        
        gmap_script = loc.find_element_by_css_selector('div.location__map').find_element_by_css_selector('iframe').get_attribute('src')
        start = gmap_script.find('!2d')

        end = gmap_script.find('!2m')

        coords = gmap_script[start + 3: end ].split('!3d')
        
        lat = coords[1]
        longit = coords[0]

        country_code = 'CA'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
    
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
