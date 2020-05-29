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

def fetch_data():
    locator_domain = 'https://www.glossier.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)
    hrefs = driver.find_elements_by_xpath('//a[contains(@href,"/locations?city")]')
    all_store_data = []
    link_list = []

    for h in hrefs:
        link_list.append(h.get_attribute('href'))

    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(5)
        
        cont = driver.find_element_by_css_selector('div.location-description').text.split('\n')
        
        location_name = cont[0]
        street_address = cont[1]
        city = '<MISSING>'
        
        hours = ''
        for c in cont[5:]:
            hours += c + ' '
            
        hours = hours.strip()
        state = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        phone_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = '<MISSING>'
        zip_code = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
