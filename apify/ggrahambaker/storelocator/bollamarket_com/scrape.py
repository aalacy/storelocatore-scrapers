import csv
import os
from sgselenium import SgSelenium

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
    city = addy[0].strip()
    state = addy[1].strip()
    zip_code = addy[2].strip()
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://www.bollamarket.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(20)

    locs = driver.find_elements_by_css_selector('div.item')

    all_store_data = []
    dup_tracker = set()

    for loc in locs:
        location_name = loc.find_element_by_css_selector('p.p-title').text
        street_address = location_name
        if street_address not in dup_tracker:
            dup_tracker.add(street_address)
        else:
            continue
        
        infos = loc.find_elements_by_css_selector('p.p-area')
        addy = infos[0].text
        if len(infos) == 2:    
            phone_number = infos[1].text.replace('Phone:', '').strip()
        else:
            phone_number = '<MISSING>'
        city, state, zip_code = addy_ext(addy)
        if state == '':
            state = '<MISSING>'
        
        store_number = loc.get_attribute('data-id')
        
        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
