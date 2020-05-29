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
    locator_domain = 'https://www.signaturestyle.com/brands/famous-hair.html'
    loc_domain = 'https://www.signaturestyle.com/'
    ext = 'salon-directory.html'

    driver = SgSelenium().chrome()
    driver.get(loc_domain + ext)

    sections = driver.find_elements_by_css_selector('div.acs-commons-resp-colctrl-row')
    state_link_list = []
    for sec in sections:
        hrefs = sec.find_elements_by_css_selector('a')
        for h in hrefs:
            state_link_list.append(h.get_attribute('href'))

    store_link_list = []
    for state_link in state_link_list:
        driver.get(state_link)
        driver.implicitly_wait(10)
        salon_groups = driver.find_elements_by_css_selector('div.salon-group')
        for group in salon_groups:
            salons = group.find_elements_by_css_selector('a')
            for salon in salons:
                store_link_list.append(salon.get_attribute('href'))

    all_store_data = []
    duplicate_checker = []
    for link in store_link_list:
        driver.get(link)
        driver.implicitly_wait(30)

        try:
            phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text
        except NoSuchElementException:
            print('closed')
            continue

        if phone_number not in duplicate_checker:
            duplicate_checker.append(phone_number)
        else:
            continue

        location_name = driver.find_element_by_css_selector('div.h2.h3').text
        location_type = driver.find_element_by_css_selector('small.sub-brand').text

        street_address = driver.find_element_by_xpath('//span[@itemprop="streetAddress"]').text
        city = driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text
        state = driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text
        zip_code = driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text
        if ' ' in zip_code:
            country_code = 'CA'
        else:
            country_code = 'US'

        geo = driver.find_element_by_xpath('//div[@itemprop="geo"]')
        lat = geo.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = geo.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')

        hours = driver.find_element_by_css_selector('div.salon-timings').text.replace('DIRECTIONS', '').replace('\n',' ').strip()
        if hours == '':
            hours = '<MISSING>'

        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, link]
    
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
