import csv
import os
from sgselenium import SgSelenium

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
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
    locator_domain = 'https://airheadsusa.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    hrefs = driver.find_elements_by_xpath('//a[contains(@href,"/hours")]')
    link_list = []
    for h in hrefs:
        link = h.get_attribute('href')
        if len(link.split('.')) == 3:
            link_list.append(link)

    all_store_data = []
    for link in link_list:
        
        driver.get(link)
        driver.implicitly_wait(5)
        
        main = driver.find_element_by_css_selector('p.p1').text.split('\n')
        
        location_name = main[0]
        
        street_address = main[1]
        
        city, state, zip_code = addy_ext(main[2])
        
        phone_number = main[3].replace('Phone:', '').strip()
        
        hours = driver.find_element_by_css_selector('div.et_pb_text_3').text.replace('\n', ' ')
        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link
        country_code = 'US'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
