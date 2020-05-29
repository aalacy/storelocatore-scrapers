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
    locator_domain = 'https://www.traderjoes.com/'
    url = 'https://locations.traderjoes.com/'

    driver = SgSelenium().chrome()
    driver.get(url)

    locs = driver.find_elements_by_css_selector('div.itemlist')

    state_list = []
    for loc in locs:
        state_url = loc.find_element_by_css_selector('a').get_attribute('href')        
        state_list.append(state_url)

    city_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        locs = driver.find_elements_by_css_selector('div.itemlist')

        for loc in locs:
            city_url = loc.find_element_by_css_selector('a').get_attribute('href')
            city_list.append(city_url)

    store_list = []
    for city in city_list:
        driver.get(city)
        driver.implicitly_wait(10)
        locs = driver.find_elements_by_css_selector('div.itemlist')

        for loc in locs:
            store_url = loc.find_element_by_css_selector('a').get_attribute('href')
            store_list.append(store_url)

    all_store_data = []
    for i, link in enumerate(store_list):
        driver.get(link)
        driver.implicitly_wait(10)
        
        street_address = driver.find_element_by_xpath('//meta[@property="business:contact_data:street_address"]').get_attribute('content')
        city = driver.find_element_by_xpath('//meta[@property="business:contact_data:locality"]').get_attribute('content')
        state = driver.find_element_by_xpath('//meta[@property="business:contact_data:region"]').get_attribute('content')
        zip_code = driver.find_element_by_xpath('//meta[@property="business:contact_data:postal_code"]').get_attribute('content').replace('â', '').strip()
        country_code = driver.find_element_by_xpath('//meta[@property="business:contact_data:country_name"]').get_attribute('content')
        phone_number = driver.find_element_by_xpath('//meta[@property="business:contact_data:phone_number"]').get_attribute('content')
        lat = driver.find_element_by_xpath('//meta[@property="place:location:latitude"]').get_attribute('content')
        longit = driver.find_element_by_xpath('//meta[@property="place:location:longitude"]').get_attribute('content')

        location_name = driver.find_element_by_css_selector('h2.h1text').text
        
        start = location_name.find('(')

        store_number = location_name[start + 1: -1]
        if not store_number.isdigit():
            store_number = '<MISSING>'

        try:
            hours_span = driver.find_element_by_xpath("//span[contains(text(),'Hours:')]")
            hours = hours_span.find_element_by_xpath("..").text.replace('Hours:', '').replace('\n', ' ').strip()
        except NoSuchElementException:
            continue
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
