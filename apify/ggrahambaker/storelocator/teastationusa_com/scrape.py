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

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    # Your scraper here

    locator_domain = 'https://teastationusa.com'

    driver = SgSelenium().chrome()
    driver.implicitly_wait(30)
    driver.get(locator_domain)

    locations = driver.find_element_by_css_selector('li.folder-collection.folder')
    all_locs = locations.find_elements_by_css_selector('li.page-collection')

    all_links = []
    for loc in all_locs:
        all_links.append(loc.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in all_links:
        driver.implicitly_wait(30)
        driver.get(link)
        content = driver.find_element_by_css_selector('div.sqs-block-content').text.split('\n')

        location_name = content[0]
        split_idx = content[1].find(',')
        street_address = content[1][:split_idx]

        rest_add = content[1][split_idx + 2:]
        if 'San Diego' in rest_add:
            rest_add = 'San Diego, CA 92115'
        elif 'Las Vegas' in rest_add:
            rest_add = 'Las Vegas, NV 89102'
        city, state, zip_code = addy_extractor(rest_add)

        phone_number = content[2].replace('Tel:', '').strip()
        hours = content[4]

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
