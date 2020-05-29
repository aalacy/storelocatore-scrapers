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

def fetch_data():
    locator_domain = 'https://toscanova.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    links = driver.find_elements_by_css_selector('a.custom-temp-btn')
    link_list = []
    for link in links:
        link_list.append(link.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        street_address = driver.find_element_by_css_selector('div.address').text
        city_state = driver.find_element_by_css_selector('div.city-state').text.split(', ')
        city = city_state[0]
        state = city_state[1]
        zip_code = driver.find_element_by_css_selector('div.zip').text
        if zip_code == '':
            zip_code = '<MISSING>'

        hours = driver.find_element_by_css_selector('div.hours').text.replace('HOURS', '').replace('\n', ' ').strip()

        phone_number = driver.find_element_by_css_selector('a#contact_us_v3_section_phone_link').text

        scripts = driver.find_elements_by_css_selector('script')
        for script in scripts:
            text = script.get_attribute('innerHTML')
            if 'var LATITUDE' in text:
                for line in text.split('\n'):
                    if line.strip().startswith("var LATITUDE"):
                        lat = driver.execute_script(line + " return LATITUDE")

                    if line.strip().startswith("var LONGITUDE"):
                        longit = driver.execute_script(line + " return LONGITUDE")

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        start = link.find('//')
        end = link.find('.to')
        location_name = link[start + 2: end]

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
