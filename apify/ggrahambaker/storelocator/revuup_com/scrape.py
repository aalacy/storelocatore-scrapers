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
    driver = SgSelenium().chrome()
    locator_domain = 'https://www.revuup.com/'
    exts = ['brewers-hill', 'mchenry-row']


    all_store_data = []
    for ext in exts:
        driver.get(locator_domain + ext)
        driver.implicitly_wait(20)
        main = driver.find_element_by_css_selector('section.studios-location')

        content = main.text.split('\n')
        location_name = content[1]
        street_address = content[2]
        city_state = content[3].split(',')
        city = city_state[0]
        state = city_state[1].strip()
        zip_code = '<MISSING>'
        phone_number = content[4]

        href = driver.find_element_by_xpath(
            '//a[@title="Open this area in Google Maps (opens a new window)"]').get_attribute('href')
        start_idx = href.find('ll=')
        end_idx = href.find('&z')
        coords = href[start_idx + 3: end_idx].split(',')

        lat = coords[0]
        longit = coords[1]

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
