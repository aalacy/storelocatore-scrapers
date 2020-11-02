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
    # Your scraper here
    locator_domain = 'https://www.dressbarn.com/'
    url = 'https://locations.dressbarn.com/index.html'

    driver = SgSelenium().chrome()
    driver.get(url)
    
    link_list = []
    state_list = []
    city_list = []

    locs = driver.find_elements_by_css_selector('a.Directory-listLink')
    
    for loc in locs:
        link = loc.get_attribute('href')
        if len(link) > 34:
            if len(link.split('/')) == 5:
                city_list.append(link)
            else:
                link_list.append(link)
            
        else:
            state_list.append(link)
        
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        locs = driver.find_elements_by_css_selector('a.Directory-listLink')
        for loc in locs:
            link = loc.get_attribute('href')

            if len(link.split('/')) == 5:
                city_list.append(link)
            else:

                link_list.append(link)
                
    for city in city_list:
        driver.get(city)
        driver.implicitly_wait(10)
        
        locs = driver.find_elements_by_css_selector('a.Teaser-titleLink')
        for loc in locs:
            link = loc.get_attribute('href')
            link_list.append(link)
    
    all_store_data = []
    for link in link_list:
        
        driver.get(link)
        driver.implicitly_wait(10)
        lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
        phone_number = driver.find_element_by_xpath('//div[@itemprop="telephone"]').text
        
        location_name = driver.find_element_by_css_selector('span#location-name').text
        store_number = driver.find_element_by_css_selector('div.Core-storeId').text.split('#')[1]
        hours = driver.find_element_by_css_selector('div.c-hours').text.replace('\n', ' ')
        
        street_address = driver.find_element_by_css_selector('span.c-address-street-1').text
        city = driver.find_element_by_css_selector('span.c-address-city').text
        state = driver.find_element_by_css_selector('abbr.c-address-state').text
        zip_code = driver.find_element_by_css_selector('span.c-address-postal-code').text
        country_code = 'US'
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
