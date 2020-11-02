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
    locator_domain = 'https://shbnet.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.view-content')
    stores = main.find_elements_by_css_selector('td')
    all_store_data = []

    for store in stores:
        content = store.text.split('\n')

        location_name = content[0]
        if len(content) == 14:
            street_address = content[2] + ' ' + content[3]
            off = 1
        elif len(content) == 13:
            street_address = content[2]
            off = 0

        city, state, zip_code = addy_ext(content[off + 3])

        phone_number = content[off + 6]
        hours = ''
        for h in content[off + 7:-2]:
            hours += h + ' '

        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
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
