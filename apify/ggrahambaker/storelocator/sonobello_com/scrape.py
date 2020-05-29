import csv
import os
from sgselenium import SgSelenium
import re

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
    locator_domain = 'https://www.sonobello.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    web_links = driver.find_element_by_css_selector('div.locations-list.card-columns').find_elements_by_css_selector(
        'a')
    links = []
    for link in web_links:
        links.append(link.get_attribute('href'))

    all_store_data = []
    for link in links:
        driver.implicitly_wait(10)
        driver.get(link)
        loc = driver.find_element_by_css_selector('div.location-info.primary-location-block')

        details = loc.text.split('\n')
        location_name = details[0]
        street_address = details[1]
        city, state, zip_code = addy_ext(details[2])
        phone_number = details[3]
        hours = ''
        for h in details[7:]:
            hours += h + ' '
        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        map = driver.find_element_by_css_selector('div#single-map')

        lat = map.get_attribute('data-lat')
        longit = map.get_attribute('data-lng')

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
