import csv
import os
from sgselenium import SgSelenium

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
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
    locator_domain = 'https://www.lynccycling.com/'
    url = 'http://lynccycling.wpengine.com/studios/'

    driver = SgSelenium().chrome()
    driver.get(url)

    all_store_data = []
    locs = driver.find_elements_by_css_selector('div.elementor-text-editor')
    names = driver.find_elements_by_css_selector('h2.elementor-heading-title')
    for i, loc in enumerate(locs):

        location_name = names[i].text

        page_url = 'http://lynccycling.wpengine.com/studios/' + location_name.lower()
        addy = loc.text.split('\n')
        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])

        phone_number = '<MISSING>'

        country_code = 'US'

        location_type = '<MISSING>'
        hours = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'
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
