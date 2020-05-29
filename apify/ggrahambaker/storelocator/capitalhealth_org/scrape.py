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
    driver = SgSelenium().chrome()

    link_list = []

    locator_domain = 'https://www.capitalhealth.org'

    for i in range(7):
        url = 'https://www.capitalhealth.org/our-locations/result?field_services_target_id=All&field_search_city_target_id=All&field_location_type_target_id=All&field_location_name_value=&page=' + str(i)
        driver.get(url)
        driver.implicitly_wait(5)
        time.sleep(3)
        
        locs = driver.find_elements_by_css_selector('div.view-empty')
        if len(locs) > 0:
            break
            
        titles = driver.find_elements_by_css_selector('h2.v-listing__title')
        
        links = [t.find_element_by_css_selector('a').get_attribute('href') for t in titles]
        
        for l in links:
            link_list.append(l)

    all_store_data = []
    for link in link_list:
        if 'multispecialty-care-lower-makefield' in link:
            continue
        driver.get(link)
        driver.implicitly_wait(5)
        time.sleep(3)
        
        location_name = driver.find_element_by_css_selector('h1').text
        
        street_address = driver.find_element_by_css_selector('span.address-line1').text
        street_address = street_address.split(',')[0]
        city = driver.find_element_by_css_selector('span.locality').text
        state = driver.find_element_by_css_selector('span.administrative-area').text
        zip_code = driver.find_element_by_css_selector('span.postal-code').text
        
        phone_number = driver.find_element_by_css_selector('div.field--name-field-phone').find_element_by_css_selector('div.field__item').text
        
        hours_div = driver.find_elements_by_css_selector('div.field--name-field-office-hours')
        if len(hours_div) == 0:
            hours = '<MISSING>'
        else:
            hours = hours_div[0].text.replace('\n', ' ')

        google_link = driver.find_elements_by_xpath('//a[contains(@href,"/maps/")]')
        if len(google_link) == 0:
            lat, longit = '<MISSING>', '<MISSING>'
        else:
            
            goog = google_link[0].get_attribute('href')
            start = goog.find('@')
            coords = goog[start + 1:].split(',')
            lat = coords[0]
            longit = coords[1]
        
        country_code = 'US'
        store_number = '<MISSING>'
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
