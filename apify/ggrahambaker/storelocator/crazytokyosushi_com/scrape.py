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
    locator_domain = 'https://crazytokyosushi.com/'
    ext_arr = ['/contact.html']

    driver = SgSelenium().chrome()

    all_store_data = []
    for ext in ext_arr:
        driver.get(locator_domain + ext)
        driver.implicitly_wait(10)

        phone = driver.find_element_by_css_selector('div.inner-phn')
        open_hours = driver.find_element_by_css_selector('div.opening-hours').text.split('\n')

        hours = ''
        for h in open_hours[2:]:
            hours += h + ' '

        lat = driver.find_element_by_xpath('//meta[@property="og:latitude"]').get_attribute('content').strip()

        longit = driver.find_element_by_xpath('//meta[@property="og:longitude"]').get_attribute('content').strip()

        phone_number = driver.find_element_by_xpath('//meta[@property="og:phone_number"]').get_attribute(
            'content').strip()

        zip_code = driver.find_element_by_xpath('//meta[@property="og:postal-code"]').get_attribute('content').strip()

        state = driver.find_element_by_xpath('//meta[@property="og:region"]').get_attribute('content').strip()

        city = driver.find_element_by_xpath('//meta[@property="og:locality"]').get_attribute('content').strip()

        street_address = driver.find_element_by_xpath('//meta[@property="og:street-address"]').get_attribute(
            'content').strip()

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        location_name = city
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
