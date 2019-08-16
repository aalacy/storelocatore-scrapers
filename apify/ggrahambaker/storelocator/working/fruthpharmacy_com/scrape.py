import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://fruthpharmacy.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#map_sidebar')
    locs = main.find_elements_by_css_selector('div.results_entry.location_primary')
    all_store_data = []
    for loc in locs:
        location_name = loc.find_element_by_css_selector('span.location_name').text
        street_address = loc.find_element_by_css_selector('span.slp_result_address.slp_result_street').text
        address = loc.find_element_by_css_selector('span.slp_result_address.slp_result_citystatezip').text.split(',')

        city = address[0]
        state = address[1].strip()
        if len(state.split(' ')) == 2:
            state_zip = state.split(' ')
            state = state_zip[0]
            zip_code = state_zip[1]
        else:
            zip_code = '<MISSING>'

        phone_number = loc.find_element_by_css_selector('span.slp_result_address.slp_result_phone').text
        hours_div = loc.find_element_by_css_selector('span.slp_result_contact.slp_result_hours.textblock').text.split(
            '\n')

        if len(hours_div) == 1:
            hours = '<MISSING>'
        else:
            hours = ''
            for h in hours_div[:3]:
                hours += h + ' '

            hours = hours.replace('Store Hours:', '').strip()

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
