import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():    
    locator_domain = 'https://www.carrabbas.com/'
    ext = 'locations/all'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('section.location-directory')
    loc_links = main.find_elements_by_css_selector('a')
    link_list = []
    for loc in loc_links:
        link = loc.get_attribute('href')
        if 'las-vegas-(w.-charleston)' in link:

            link = 'https://www.carrabbas.com/locations/nv/las-vegas-(w-charleston)'

        if '/fl/oviedo' in link:
            link = 'https://www.carrabbas.com/locations/fl/winter-springs-(oviedo)'
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        source = str(driver.page_source)

        for line in source.splitlines():
            if line.strip().startswith("$(function(){initLocationDetail(false,"):
                raw_line = line.strip()
        
                start_lat = raw_line.find('"Latitude":')
                start_string = raw_line[start_lat + len('"Latitude":'):]
                end_lat = start_string.find(',')
                
                lat = start_string[1:end_lat - 1]
                
                start_longit = raw_line.find('"Longitude":')
                start_string = raw_line[start_longit + len('"Longitude":'):]
                end_longit = start_string.find(',')

                longit = start_string[1:end_longit - 1]
                
        try:
            location_name = driver.find_element_by_xpath('//h3[@itemprop="name"]').text
        except NoSuchElementException:
            continue
        
        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text
        
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text
        
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text
        
        phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text
        if len(phone_number) == 11:
            phone_number = '<MISSING>'
        
        main_loc = driver.find_element_by_css_selector('section.l-location-details.desktop-only')
        hours = main_loc.find_elements_by_css_selector('p')[1].text.replace('\n', ' ').split('Happy')[0].strip()
        
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
