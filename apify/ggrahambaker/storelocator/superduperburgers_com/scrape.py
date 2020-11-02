import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url", "operating_info"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(addy_string):
    addy = addy_string.split(',')
    if len(addy) == 3:
        street_address = addy[0]
        city = addy[1].strip()
        state_zip = addy[2].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
    else:
        street_address = addy[0] + ' ' + addy[1].strip()
        city = addy[2].strip()
        state_zip = addy[3].strip().split(' ')
        state = state_zip[0]
        zip_code = state_zip[1]
        
    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.superduperburgers.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    #driver.find_element_by_css_selector('button.link-button').click()
    driver.implicitly_wait(5)
    all_store_data = []

    locs = driver.find_elements_by_css_selector('div.locationListItem')

    for loc in locs:
        location_name = loc.find_element_by_css_selector('h3.location-name').text
        a_tags = loc.find_elements_by_css_selector('a')
        page_url = a_tags[0].get_attribute('href')
        addy = a_tags[1].text

        hrefs = loc.find_elements_by_css_selector('a')
        phone_number = ''
        for href in hrefs:
            if 'tel:' in href.get_attribute('href'):
                phone_number = href.text
                break

        if phone_number == '':
            phone_number = '<MISSING>'
     
        street_address, city, state, zip_code = parse_address(addy)
        
        hours = loc.find_element_by_css_selector('div.locationListItemHours').text.replace('\n', ' ')
        if 'Closed until further notice' in hours:
            operating_info = 'Closed until further notice'
        elif 'Temporarily closed until' in hours:
            operating_info = 'Temporarily closed until further notice.'
        elif 'Open during' in hours:
            operating_info = 'Open during Stadium Events'
        else:
            operating_info = 'Open'
            
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url, operating_info]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
