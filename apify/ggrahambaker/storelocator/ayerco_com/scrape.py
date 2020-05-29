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

    if len(state_zip) == 2:
        state = state_zip[0]
        zip_code = state_zip[1]
    else:
        state = state_zip[0]
        zip_code = state_zip[2]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://ayerco.com/'
    ext = 'stores.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main_list = driver.find_element_by_css_selector('tbody').find_elements_by_css_selector('tr')[2:]
    all_store_data = []
    for store in main_list:

        cols = store.find_elements_by_css_selector('td')
        if len(cols) == 1:
            break

        store_number = cols[0].text.replace('Ayerco', '').strip()[:2]

        street_address = cols[1].text
        city, state, zip_code = addy_ext(cols[2].text)

        phone_number = cols[3].text

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        location_name = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
