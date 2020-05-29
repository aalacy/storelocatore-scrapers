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
    locator_domain = 'https://www.freedomoil.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    all_store_data = []
    locs = driver.find_elements_by_css_selector('div.media.image-left.medium')
    print(len(locs))
    for loc in locs:
        content = loc.text.split('\n')
        street_address = content[0]
        address = content[1].split(',')
        city = address[0]
        state = address[1].strip()
        if '52707' in state:
            state = 'Illinois'
            zip_code = '<MISSING>'
        else:
            zip_code = '<MISSING>'
        href = loc.find_element_by_css_selector('a').get_attribute('href')
        start_idx = href.find('/@')
        end_idx = href.find('z/data')

        coords = href[start_idx + 2:end_idx].split(',')
        lat = coords[0]
        longit = coords[1]

        phone_number = '<MISSING>'
        location_name = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
