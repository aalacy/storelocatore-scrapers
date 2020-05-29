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
    locator_domain = 'https://www.marlofurniture.com/'
    ext = 'pages/store-locator'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    stores = driver.find_elements_by_css_selector('div.location-header')
    for store in stores:
        content = store.text.split('\n')
        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[3]

        hours = 'Monday - Saturday 10 am to 9 pm Sunday 11 am to 7 pm'

        if 'Distribution' in location_name:
            location_type = 'Distribution Center'
        else:
            location_type = 'Store'

        country_code = 'US'

        store_number = '<MISSING>'

        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
