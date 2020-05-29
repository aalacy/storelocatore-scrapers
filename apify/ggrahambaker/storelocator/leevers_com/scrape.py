import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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
    locator_domain = 'http://leevers.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    locs = driver.find_element_by_css_selector('section#locate').find_elements_by_css_selector('div')
    all_store_data = []
    for loc in locs:
        ps = loc.find_elements_by_css_selector('p')

        location_name = ps[0].text
        street_address = ps[1].text
        city, state, zip_code = addy_ext(ps[2].text)
        phone_number = ps[3].text.replace('PH:', '').strip()

        country_code = 'US'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
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
