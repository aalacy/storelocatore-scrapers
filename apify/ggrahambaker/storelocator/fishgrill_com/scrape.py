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
    locator_domain = 'https://fishgrill.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    locs = driver.find_elements_by_css_selector('div.location-middal-part')

    all_store_data = []
    for loc in locs:
        content = loc.text.split('\n')
        location_name = content[0]
        if '6834 Route 9' in content[1]:
            street_address = '6834 Route 9 S.'
            city = 'Howell'
            state = 'NJ'
            zip_code = '07731'
        else:
            address = content[1].split(',')
            street_address = address[0]
            city = address[1].strip()
            state_zip = address[2].strip().split(' ')
            state = state_zip[0]
            zip_code = state_zip[1]
            if 'S' in zip_code:
                zip_code = zip_code.replace('S','5')
            zip_code = zip_code.replace('.', '')

        phone_number = content[2]
        hours = content[3]

        href = loc.find_element_by_css_selector('iframe').get_attribute('src')
        start_idx = href.find('!2d')
        end_idx = href.find('!2m')
        if start_idx > 0:
            coords = href[start_idx + 3:end_idx].split('!3d')
            longit = coords[0]
            lat = coords[1]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
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
