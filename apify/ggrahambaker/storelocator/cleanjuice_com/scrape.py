import csv
import os
from sgselenium import SgSelenium
import re

def addy_ext(addy):
    address = addy.split(',')
    if len(address) == 1:
        city = '<MISSING>'
        state_zip = address[0].strip().split(' ')
    else:
        city = address[0]
        state_zip = address[1].strip().split(' ')
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
    locator_domain = 'https://cleanjuice.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main_div = driver.find_element_by_css_selector('div.et_pb_row.et_pb_row_2')
    atags = main_div.find_elements_by_css_selector('a')
    href_arr = []
    for tag in atags:
        href_arr.append(tag.get_attribute('href'))

    all_store_data = []
    for href in href_arr:
        driver.implicitly_wait(10)
        driver.get(href)
        elements = driver.find_elements_by_css_selector('div.et_pb_column')
        for element in elements:
            buttons = element.find_elements_by_css_selector('div.et_pb_button_module_wrapper')
            if len(buttons) == 1:
                page_url = buttons[0].find_element_by_css_selector('a').get_attribute('href')
            else:
                continue

            content = element.text.split('\n')
            if len(content) > 5:
                location_name = content[0]
                street_address = content[2]

                phone_number = content[4]
                
                if 'COMING SOON' in phone_number:
                    continue

                if 'CLOSED' in content[3]:
                    continue

                if len(content[3].split(',')) == 3:
                    temp_addy = content[3].split(',')
                    street_address += ' ' + temp_addy[0]
                    other_addy = temp_addy[1].strip() + ',' + temp_addy[2]

                    city, state, zip_code = addy_ext(other_addy)
                elif 'TX,' in content[3]:
                    temp_addy = content[3].split(',')
                    city_state = temp_addy[0].split(' ')
                    city = city_state[0]
                    state = city_state[1]
                    zip_code = temp_addy[1].strip()

                else:
                    city, state, zip_code = addy_ext(content[3])

                if 'COMING' in phone_number:
                    phone_number = '<MISSING>'

                hours_arr = content[5:]
                hours = ''
                for ele in hours_arr:
                    hours += ele + ' '
                hours = hours.strip()

                country_code = 'US'
                store_number = '<MISSING>'
                location_type = '<MISSING>'
                lat = '<MISSING>'
                longit = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours, page_url]

                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
