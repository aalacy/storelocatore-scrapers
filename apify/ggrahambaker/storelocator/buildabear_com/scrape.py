import csv
import os
from sgselenium import SgSelenium
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import time
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('buildabear_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.buildabear.com/'
    ext = 'stores-sitemap'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    element = driver.find_element_by_css_selector('button.age-continue')
    driver.execute_script("arguments[0].click();", element)

    main = driver.find_element_by_css_selector('div.sitemap-list')
    hrefs = main.find_elements_by_css_selector('a')

    # us locations
    link_list = []
    for h in hrefs:
        link_list.append(h.get_attribute('href'))

    # canada locations
    canada_cities = ['vancouver', 'calgary', 'edmonton', 'winnipeg', 'toronto', 'ottowa', 'nova scotia']
    driver.get('https://www.buildabear.com/storefinder')
    driver.implicitly_wait(10)

    select = Select(driver.find_element_by_id('distance'))
    # select by value
    select.select_by_value('50')

    for c_city in canada_cities:
        input_loc = driver.find_element_by_id("address")
        input_loc.send_keys(c_city)
        input_loc.submit()
        driver.implicitly_wait(10)
        time.sleep(1)

        loc_hrefs = driver.find_elements_by_xpath("//a[contains(@href, '/locations?StoreID')]")

        if len(loc_hrefs) == 0:
            continue
        for loc in loc_hrefs:
            link = loc.get_attribute('href')
            if link not in link_list:
                link_list.append(link)

        input_loc.clear()
        time.sleep(1)

    all_store_data = []
    for i, link in enumerate(link_list):
        logger.info(i, link)
        driver.get(link)
        driver.implicitly_wait(10)

        loc_j = driver.find_elements_by_xpath('//script[@type="application/ld+json"]')
        loc_json = json.loads(loc_j[1].get_attribute('innerHTML'))
        addy = loc_json['address']

        location_name = loc_json['name']
        if 'CLOSED' in location_name:
            continue
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode'].strip()
        if len(zip_code) == 9:
            zip_code = zip_code[:5] + '-' + zip_code[5:]
        if len(zip_code.split(' ')) == 2:
            country_code = 'CA'
        else:
            if len(zip_code) == 6:
                country_code = 'CA'
            else:

                country_code = 'US'

        coords = loc_json['geo']
        lat = coords['latitude']
        longit = coords['longitude']

        phone_number = loc_json['telephone']
        hours = driver.find_element_by_css_selector('div#storeHours').text.replace('\n', ' ')

        location_type = '<MISSING>'
        page_url = link
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
