import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://www.kayasushi.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)
    link_list = ['http://www.kayasushi.com/mdr', 'http://www.kayasushi.com/es']

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        location_name = driver.find_element_by_css_selector('h1').text

        bodys = driver.find_elements_by_xpath('//div[@data-menu-name="PREVIEW_BODY"]')
        address = bodys[0].text.split('\n')
        street_address = address[0]
        city, state, zip_code = addy_ext(address[1])

        phone_number = bodys[1].text.replace('PHONE:', '').strip()

        hours = driver.find_elements_by_css_selector('h3')[1].text.replace('\n', ' ')

        country_code = 'US'
        longit = '<MISSING>'
        lat = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
