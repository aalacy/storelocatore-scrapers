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
    # Your scraper here

    locator_domain = 'https://www.cowboymaloneys.com/'
    ext = 'store_finder.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locations = driver.find_elements_by_css_selector('div.location-result')
    link_arr = []
    for location in locations:
        link_arr.append(location.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_arr:
        driver.implicitly_wait(10)
        driver.get(link)
        loc_div = driver.find_element_by_css_selector('div#location-address-section')
        location_name = loc_div.find_element_by_css_selector('h2').text
        address = loc_div.find_element_by_css_selector('address').text.split('\n')
        street_address = address[0]
        city, state, zip_code = addy_ext(address[1])
        phone_number = driver.find_element_by_css_selector('div#location-phone-section').text.replace('Phone',
                                                                                                      '').strip()
        hours = driver.find_element_by_css_selector('div#location-hours-section').text.replace('Hours', '').replace(
            '\n', ' ')

        lat = '<MISSING>'
        longit = '<MISSING>'

        country_code = 'US'
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
